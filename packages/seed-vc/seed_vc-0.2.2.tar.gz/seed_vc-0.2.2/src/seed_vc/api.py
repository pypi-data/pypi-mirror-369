from __future__ import annotations

import os
import time

from types import SimpleNamespace
from typing import Optional, Tuple

import numpy as np
import torch
import torchaudio
import soundfile as sf
import librosa

from .Models.audio import AudioData
from .inference import load_models as load_models_v1, adjust_f0_semitones, crossfade
from .inference_v2 import load_v2_models


# Reuse the same device policy as the inference scripts
if torch.cuda.is_available():
    _device = torch.device("cuda")
elif torch.backends.mps.is_available():
    _device = torch.device("mps")
else:
    _device = torch.device("cpu")


@torch.no_grad()
def inference(
    source: AudioData,
    target: AudioData,
    output: Optional[str] = None,
    diffusion_steps: int = 30,
    length_adjust: float = 1.0,
    inference_cfg_rate: float = 0.7,
    f0_condition: bool = False,
    auto_f0_adjust: bool = False,
    semi_tone_shift: int = 0,
    checkpoint: Optional[str] = None,
    config: Optional[str] = None,
    fp16: bool = True,
) -> Tuple[int, np.ndarray]:
    """
    Run Seed-VC V1 inference given in-memory audio.

    Returns: (sample_rate, waveform_np)
    Optionally writes a file if `output` directory is provided.
    """
    # Build an args-like namespace for loader
    args = SimpleNamespace(
        f0_condition=f0_condition,
        checkpoint=checkpoint,
        config=config,
        fp16=fp16,
    )

    model, semantic_fn, f0_fn, vocoder_fn, campplus_model, mel_fn, mel_fn_args = load_models_v1(args)
    sr = int(mel_fn_args["sampling_rate"])  # 22050 or 44100 depending on f0_condition

    # Prepare source/target audio at model SR
    def _to_tensor_at_sr(wave: np.ndarray, orig_sr: int, target_sr: int) -> torch.Tensor:
        if orig_sr != target_sr:
            wave = librosa.resample(wave, orig_sr, target_sr)
        wave_t = torch.tensor(wave, dtype=torch.float32, device=_device)[None, :]
        return wave_t

    # Limit target to 25s like CLI (context len - safety)
    source_wave_t = _to_tensor_at_sr(np.asarray(source.samples), int(source.sample_rate), sr)
    target_wave_t = _to_tensor_at_sr(np.asarray(target.samples), int(target.sample_rate), sr)
    target_wave_t = target_wave_t[:, : sr * 25]

    # Resample to 16k for content (Whisper/xlsr)
    converted_waves_16k = torchaudio.functional.resample(source_wave_t, sr, 16000)
    if converted_waves_16k.size(-1) <= 16000 * 30:
        S_alt = semantic_fn(converted_waves_16k)
    else:
        overlapping_time = 5
        S_alt_list = []
        buffer = None
        traversed_time = 0
        while traversed_time < converted_waves_16k.size(-1):
            if buffer is None:
                chunk = converted_waves_16k[:, traversed_time : traversed_time + 16000 * 30]
            else:
                chunk = torch.cat(
                    [buffer, converted_waves_16k[:, traversed_time : traversed_time + 16000 * (30 - overlapping_time)]],
                    dim=-1,
                )
            S_chunk = semantic_fn(chunk)
            if traversed_time == 0:
                S_alt_list.append(S_chunk)
            else:
                S_alt_list.append(S_chunk[:, 50 * overlapping_time :])
            buffer = chunk[:, -16000 * overlapping_time :]
            traversed_time += 30 * 16000 if traversed_time == 0 else chunk.size(-1) - 16000 * overlapping_time
        S_alt = torch.cat(S_alt_list, dim=1)

    ori_waves_16k = torchaudio.functional.resample(target_wave_t, sr, 16000)
    S_ori = semantic_fn(ori_waves_16k)

    # Mels
    mel = mel_fn(source_wave_t.float())
    mel2 = mel_fn(target_wave_t.float())

    hop_length = int(mel_fn_args["hop_size"])  # 256 or 512
    max_context_window = sr // hop_length * 30
    overlap_frame_len = 16
    overlap_wave_len = overlap_frame_len * hop_length

    target_lengths = torch.LongTensor([int(mel.size(2) * length_adjust)]).to(mel.device)
    target2_lengths = torch.LongTensor([mel2.size(2)]).to(mel2.device)

    # Style vector via CAMPPlus on 16k fbank
    feat2 = torchaudio.compliance.kaldi.fbank(
        ori_waves_16k, num_mel_bins=80, dither=0, sample_frequency=16000
    )
    feat2 = feat2 - feat2.mean(dim=0, keepdim=True)
    style2 = campplus_model(feat2.unsqueeze(0))

    # F0
    if f0_condition:
        F0_ori = f0_fn(ori_waves_16k[0], thred=0.03)
        F0_alt = f0_fn(converted_waves_16k[0], thred=0.03)
        F0_ori = torch.from_numpy(F0_ori).to(_device)[None]
        F0_alt = torch.from_numpy(F0_alt).to(_device)[None]
        voiced_F0_ori = F0_ori[F0_ori > 1]
        voiced_F0_alt = F0_alt[F0_alt > 1]
        log_f0_alt = torch.log(F0_alt + 1e-5)
        voiced_log_f0_ori = torch.log(voiced_F0_ori + 1e-5)
        voiced_log_f0_alt = torch.log(voiced_F0_alt + 1e-5)
        median_log_f0_ori = torch.median(voiced_log_f0_ori)
        median_log_f0_alt = torch.median(voiced_log_f0_alt)
        shifted_log_f0_alt = log_f0_alt.clone()
        if auto_f0_adjust:
            shifted_log_f0_alt[F0_alt > 1] = log_f0_alt[F0_alt > 1] - median_log_f0_alt + median_log_f0_ori
        shifted_f0_alt = torch.exp(shifted_log_f0_alt)
        if semi_tone_shift != 0:
            shifted_f0_alt[F0_alt > 1] = adjust_f0_semitones(shifted_f0_alt[F0_alt > 1], semi_tone_shift)
    else:
        F0_ori = None
        shifted_f0_alt = None

    # Length regulation -> conditions
    cond, _, _, _, _ = model.length_regulator(
        S_alt, ylens=target_lengths, n_quantizers=3, f0=shifted_f0_alt
    )
    prompt_condition, _, _, _, _ = model.length_regulator(
        S_ori, ylens=target2_lengths, n_quantizers=3, f0=F0_ori
    )

    # Chunked generation with crossfade
    processed_frames = 0
    generated_wave_chunks = []
    start_time = time.time()
    while processed_frames < cond.size(1):
        max_source_window = max_context_window - mel2.size(2)
        chunk_cond = cond[:, processed_frames : processed_frames + max_source_window]
        is_last_chunk = processed_frames + max_source_window >= cond.size(1)
        cat_condition = torch.cat([prompt_condition, chunk_cond], dim=1)
        with torch.autocast(device_type=_device.type, dtype=torch.float16 if fp16 else torch.float32):
            vc_target = model.cfm.inference(
                cat_condition,
                torch.LongTensor([cat_condition.size(1)]).to(mel2.device),
                mel2,
                style2,
                None,
                diffusion_steps,
                inference_cfg_rate=inference_cfg_rate,
            )
            vc_target = vc_target[:, :, mel2.size(-1) :]
        vc_wave = vocoder_fn(vc_target.float()).squeeze()[None]
        if processed_frames == 0:
            if is_last_chunk:
                output_wave = vc_wave[0].cpu().numpy()
                generated_wave_chunks.append(output_wave)
                break
            output_wave = vc_wave[0, :-overlap_wave_len].cpu().numpy()
            generated_wave_chunks.append(output_wave)
            previous_chunk = vc_wave[0, -overlap_wave_len:]
            processed_frames += vc_target.size(2) - overlap_frame_len
        elif is_last_chunk:
            output_wave = crossfade(previous_chunk.cpu().numpy(), vc_wave[0].cpu().numpy(), overlap_wave_len)
            generated_wave_chunks.append(output_wave)
            processed_frames += vc_target.size(2) - overlap_frame_len
            break
        else:
            output_wave = crossfade(
                previous_chunk.cpu().numpy(), vc_wave[0, :-overlap_wave_len].cpu().numpy(), overlap_wave_len
            )
            generated_wave_chunks.append(output_wave)
            previous_chunk = vc_wave[0, -overlap_wave_len:]
            processed_frames += vc_target.size(2) - overlap_frame_len

    vc_wave_np = np.concatenate(generated_wave_chunks)
    elapsed = time.time() - start_time
    if vc_wave_np.size > 0:
        print(f"RTF: {elapsed / vc_wave_np.size * sr}")

    # Optionally save
    if output:
        os.makedirs(output, exist_ok=True)
        src_name = getattr(source.metadata, "name", "source") if getattr(source, "metadata", None) else "source"
        tgt_name = getattr(target.metadata, "name", "target") if getattr(target, "metadata", None) else "target"
        out_path = os.path.join(
            output,
            f"vc_{src_name}_{tgt_name}_{length_adjust}_{diffusion_steps}_{inference_cfg_rate}.wav",
        )
        sf.write(out_path, vc_wave_np, sr)

    return sr, vc_wave_np


@torch.no_grad()
def inference_v2(
    source: AudioData,
    target: AudioData,
    output: Optional[str] = None,
    diffusion_steps: int = 30,
    length_adjust: float = 1.0,
    intelligibility_cfg_rate: float = 0.7,
    similarity_cfg_rate: float = 0.7,
    top_p: float = 0.9,
    temperature: float = 1.0,
    repetition_penalty: float = 1.0,
    convert_style: bool = False,
    anonymization_only: bool = False,
    compile: bool = False,
    ar_checkpoint_path: Optional[str] = None,
    cfm_checkpoint_path: Optional[str] = None,
) -> Tuple[int, np.ndarray]:
    """
    Run Seed-VC V2 inference given in-memory audio (uses the v2 wrapper under the hood).

    Returns: (sample_rate, waveform_np)
    Optionally writes a file if `output` directory is provided.
    """
    # Build args for v2 loader and conversion call
    args = SimpleNamespace(
        diffusion_steps=diffusion_steps,
        length_adjust=length_adjust,
        intelligibility_cfg_rate=intelligibility_cfg_rate,
        similarity_cfg_rate=similarity_cfg_rate,
        top_p=top_p,
        temperature=temperature,
        repetition_penalty=repetition_penalty,
        convert_style=convert_style,
        anonymization_only=anonymization_only,
        compile=compile,
        ar_checkpoint_path=ar_checkpoint_path,
        cfm_checkpoint_path=cfm_checkpoint_path,
    )

    # Ensure models are loaded
    from . import inference_v2 as _infv2
    if _infv2.vc_wrapper_v2 is None:
        _infv2.vc_wrapper_v2 = load_v2_models(args)

    # Call the in-memory V2 wrapper directly
    sr_v2, audio_np = _infv2.vc_wrapper_v2.convert_voice_with_streaming_arrays(
        source_wave=np.asarray(source.samples),
        target_wave=np.asarray(target.samples),
        source_sr=int(source.sample_rate),
        target_sr=int(target.sample_rate),
        diffusion_steps=diffusion_steps,
        length_adjust=length_adjust,
        intelligebility_cfg_rate=intelligibility_cfg_rate,
        similarity_cfg_rate=similarity_cfg_rate,
        top_p=top_p,
        temperature=temperature,
        repetition_penalty=repetition_penalty,
        convert_style=convert_style,
        anonymization_only=anonymization_only,
        device=_device,
        dtype=torch.float16,
        stream_output=False,
    )

    # Optionally save
    if output:
        os.makedirs(output, exist_ok=True)
        src_name = getattr(source.metadata, "name", "source") if getattr(source, "metadata", None) else "source"
        tgt_name = getattr(target.metadata, "name", "target") if getattr(target, "metadata", None) else "target"
        out_path = os.path.join(
            output,
            f"vc_v2_{src_name}_{tgt_name}_{length_adjust}_{diffusion_steps}_{similarity_cfg_rate}.wav",
        )
        sf.write(out_path, audio_np, sr_v2)

    return sr_v2, audio_np

