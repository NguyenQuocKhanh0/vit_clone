import torch  # isort:skip
from tfloader import load_tfdata
import json
from types import SimpleNamespace
from models import SynthesizerTrn, DurationNet
import matplotlib.pyplot as plt
from scipy.io import wavfile
import time
# global config
config_file = "config.json"
duration_model_path = "/mnt/g/download/Audio_mienNam/vbx_duration_model.pth"
vits_model_path = "/mnt/c/Users/ADMIN/Downloads/ckpt_00028000.pth"
output_file = "clip3.wav"
device = "cpu"
with open(config_file, "rb") as f:
    hps = json.load(f, object_hook=lambda x: SimpleNamespace(**x))
def text_to_phone_idx(text):
    # lowercase
    text = text.lower()
    # unicode normalize
    text = unicodedata.normalize("NFKC", text)
    text = text.replace(".", " . ")
    text = text.replace(",", " , ")
    text = text.replace(";", " ; ")
    text = text.replace(":", " : ")
    text = text.replace("!", " ! ")
    text = text.replace("?", " ? ")
    text = text.replace("(", " ( ")

#     text = num_re.sub(r" \1 ", text)
    words = text.split()
#     words = [read_number(w) if num_re.fullmatch(w) else w for w in words]
    text = " ".join(words)

    # remove redundant spaces
    text = re.sub(r"\s+", " ", text)
    # remove leading and trailing spaces
    text = text.strip()
    # convert words to phone indices
    tokens = []
    for c in text:
        # if c is "," or ".", add <sil> phone
        if c in ":,.!?;(":
            tokens.append(sil_idx)
        elif c in phone_set:
            tokens.append(phone_set.index(c))
        elif c == " ":
            # add <sep> phone
            tokens.append(0)
    if tokens[0] != sil_idx:
        # insert <sil> phone at the beginning
        tokens = [sil_idx, 0] + tokens
    if tokens[-1] != sil_idx:
        tokens = tokens + [0, sil_idx]
    return tokens
duration_net = DurationNet(hps.data.vocab_size, 64, 4).to(device)
duration_net.load_state_dict(torch.load(duration_model_path, map_location=device))
duration_net = duration_net.eval()
generator = SynthesizerTrn(
    hps.data.vocab_size,
    hps.data.filter_length // 2 + 1,
    hps.train.segment_size // hps.data.hop_length,
    **vars(hps.model)
).to(device)
del generator.enc_q
ckpt = torch.load(vits_model_path, map_location=device)
params = {}
for k, v in ckpt["net_g"].items():
    k = k[7:] if k.startswith("module.") else k
    params[k] = v
generator.load_state_dict(params, strict=False)
del ckpt, params
generator = generator.eval()

import unicodedata
import re
import regex
import numpy as np
phone_set_file = "/mnt/g/download/Audio_mienNam/vbx_phone_set.json"
with open(phone_set_file, "r") as f:
    phone_set = json.load(f)

assert phone_set[0][1:-1] == "SEP"
assert "sil" in phone_set
sil_idx = phone_set.index("sil")

space_re = regex.compile(r"\s+")
number_re = regex.compile("([0-9]+)")
digits = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
num_re = regex.compile(r"([0-9.,]*[0-9])")
alphabet = "aàáảãạăằắẳẵặâầấẩẫậeèéẻẽẹêềếểễệiìíỉĩịoòóỏõọôồốổỗộơờớởỡợuùúủũụưừứửữựyỳýỷỹỵbcdđghklmnpqrstvx"
keep_text_and_num_re = regex.compile(rf"[^\s{alphabet}.,0-9]")
keep_text_re = regex.compile(rf"[^\s{alphabet}]")
phone_idx = text_to_phone_idx("ê")
batch = {
    "phone_idx": np.array([phone_idx]),
    "phone_length": np.array([len(phone_idx)]),
}
phone_length = torch.from_numpy(batch["phone_length"].copy()).long().to(device)
phone_idx = torch.from_numpy(batch["phone_idx"].copy()).long().to(device)
demo1=time.time()
with torch.inference_mode():
    phone_duration = duration_net(phone_idx, phone_length)[:, :, 0] * 1000
phone_duration = torch.where(
    phone_idx == sil_idx, torch.clamp_min(phone_duration, 200), phone_duration
)
phone_duration = torch.where(phone_idx == 0, 0, phone_duration)

# generate waveform
end_time = torch.cumsum(phone_duration, dim=-1)
start_time = end_time - phone_duration
start_frame = start_time / 1000 * hps.data.sampling_rate / hps.data.hop_length
end_frame = end_time / 1000 * hps.data.sampling_rate / hps.data.hop_length
spec_length = end_frame.max(dim=-1).values
pos = torch.arange(0, spec_length.item(), device=device)
attn = torch.logical_and(
    pos[None, :, None] >= start_frame[:, None, :],
    pos[None, :, None] < end_frame[:, None, :],
).float()
with torch.inference_mode():
    y_hat = generator.infer(
        phone_idx, phone_length, spec_length, attn, max_len=None, noise_scale=0.667
    )[0]
y_hat = y_hat[0, 0].data.cpu().numpy()
demo2=time.time()
print(demo2-demo1)
wavfile.write(output_file, hps.data.sampling_rate, y_hat)

# /mnt/c/Users/ADMIN/Desktop/Vits_clone/light-speed