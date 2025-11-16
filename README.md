---
library_name: transformers
pipeline_tag: text-generation
base_model:
- aisingapore/Llama-SEA-LION-v3-8B-IT
language:
- en
- zh
- vi
- id
- th
- fil
- ta
- ms
- km
- lo
- my
- jv
- su
license: llama3.1
---

<div>
  <img src="llama_sea_lion_3.5_8b_r_banner.png"/>
</div>

Current Version: `14.04.2025`

# Llama-SEA-LION-v3.5-8B-R

[SEA-LION](https://arxiv.org/abs/2504.05747) is a collection of Large Language Models (LLMs) which have been pretrained and instruct-tuned for the Southeast Asia (SEA) region.

SEA-LION stands for _Southeast Asian Languages In One Network_.

- **Developed by:** Products Pillar, AI Singapore
- **Funded by:** Singapore NRF
- **Model type:** Decoder
- **Languages supported:** Burmese, Chinese, English, Filipino, Indonesia, Javanese, Khmer, Lao, Malay, Sundanese, Tamil, Thai, Vietnamese
- **License:** [Llama 3.1 Community License](https://huggingface.co/meta-llama/Llama-3.1-70B-Instruct/blob/main/LICENSE)

## Model Details
### Model Description

Llama-SEA-LION-v3.5-8B-R is a hybrid model offering versatile functionality, handling both complex reasoning tasks and general text generation, with mode selection managed through the tokenizer's chat template.

We performed instruction tuning in English and also in SEA languages such as Filipino, Indonesian, Tamil, Thai and Vietnamese on our [continued pre-trained Llama-SEA-LION-v3-8B](https://huggingface.co/aisingapore/Llama-SEA-LION-v3-8B), a decoder model using the Llama 3.1 architecture, to create Llama-SEA-LION-v3.5-8B-R.

For tokenisation, the model employs the default tokenizer used in Llama 3.1 70B Instruct. The model has a context length of 128k.

### Benchmark Performance
We evaluated Llama-SEA-LION-v3.5-8B-R on both general language capabilities and instruction-following capabilities.

#### General Language Capabilities
For the evaluation of general language capabilities, we employed the [SEA-HELM evaluation benchmark](https://arxiv.org/abs/2502.14301) across a variety of tasks.
These tasks include Question Answering (QA), Sentiment Analysis (Sentiment), Toxicity Detection (Toxicity), Translation in both directions (Eng>Lang & Lang>Eng), Abstractive Summarisation (Abssum), Causal Reasoning (Causal), Natural Language Inference (NLI), and linguistic diagnostics (LINDSEA).

Note: SEA-HELM is implemented using prompts to elicit answers in a strict format. For all tasks, the model is expected to provide an answer tag from which the answer is automatically extracted. For tasks where options are provided, the answer should comprise one of the pre-defined options. The scores for each task is normalised to account for baseline performance due to random chance.

The evaluation was done **zero-shot** with native prompts on a sample of 100-1000 instances for each dataset.

#### Instruction-following Capabilities
Since Llama-SEA-LION-v3.5-8B-R is an instruction-following model, we also evaluated it on instruction-following capabilities with two datasets, SEA-IFEval (based on [IFEval](https://arxiv.org/abs/2311.07911)) and SEA-MTBench (based on [MT-Bench](https://arxiv.org/abs/2306.05685)).

As these two datasets were originally in English, the linguists and native speakers in the team worked together to filter, localise and translate the datasets into the respective target languages to ensure that the examples remained reasonable, meaningful and natural.

**SEA-IFEval**

SEA-IFEval evaluates a model's ability to adhere to constraints provided in the prompt, for example beginning a response with a specific word/phrase or answering with a certain number of sections. Additionally, accuracy is normalised by the proportion of responses in the correct language (if the model performs the task correctly but responds in the wrong language, it is judged to have failed the task).

**SEA-MTBench**

SEA-MTBench evaluates a model's ability to engage in multi-turn (2 turns) conversations and respond in ways that align with human needs. We use `gpt-4-1106-preview` as the judge model and compare against `gpt-3.5-turbo-0125` as the baseline model. The metric used is the weighted win rate against the baseline model (i.e. average win rate across each category: Math, Reasoning, STEM, Humanities, Roleplay, Writing, Extraction). A tie is given a score of 0.5.

For more details on Llama-SEA-LION-v3.5-8B-R benchmark performance, please refer to the SEA-HELM leaderboard, https://leaderboard.sea-lion.ai/.

### Usage
Llama-SEA-LION-v3.5-8B-R can be run using the 🤗 Transformers library 
```python
import transformers
import torch

model_id = "aisingapore/Llama-SEA-LION-v3.5-8B-R"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
)
messages = [
    {"role": "user", "content": "Apa sentimen dari kalimat berikut ini?\nKalimat: Buku ini sangat membosankan.\nJawaban: "},
]

outputs = pipeline(
    messages,
    max_new_tokens=256,
)
print(outputs[0]["generated_text"][-1])
```

### Thinking Mode Toggle
Llama-SEA-LION-v3.5-8B-R defaults to reasoning with `thinking_mode="on"` passed to the chat template. To use non-thinking mode ie. standard generations, pass `thinking_mode="off"` to the chat template instead.
```python
import transformers
import torch

model_id = "aisingapore/Llama-SEA-LION-v3.5-8B-R"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
)

tokenizer = pipeline.tokenizer

messages = [
    {"role": "user", "content": "Apa sentimen dari kalimat berikut ini?\nKalimat: Buku ini sangat membosankan.\nJawaban: "},
]

prompt = tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False, thinking_mode="off")

outputs = pipeline(
    prompt,
    max_new_tokens=256,
)

print(outputs[0]["generated_text"])
```

### Caveats
It is important for users to be aware that our model exhibits certain limitations that warrant consideration. Like many LLMs, the model can hallucinate and occasionally generates irrelevant content, introducing fictional elements that are not grounded in the provided context. Users should also exercise caution in interpreting and validating the model's responses due to the potential inconsistencies in its reasoning.

## Limitations
### Safety
Current SEA-LION models, including this commercially permissive release, have not been aligned for safety. Developers and users should perform their own safety fine-tuning and related security measures. In no event shall the authors be held liable for any claim, damages, or other liability arising from the use of the released weights and codes.

## Call for Contributions
We encourage researchers, developers, and language enthusiasts to actively contribute to the enhancement and expansion of SEA-LION. Contributions can involve identifying and reporting bugs, sharing pre-training, instruction, and preference data, improving documentation usability, proposing and implementing new model evaluation tasks and metrics, or training versions of the model in additional Southeast Asian languages. Join us in shaping the future of SEA-LION by sharing your expertise and insights to make these models more accessible, accurate, and versatile. Please check out our GitHub for further information on the call for contributions.

## The Team
Antonyrex Sajeban, Chan Adwin, Cheng Nicholas, Choa Esther, Huang Yuli, Hulagadri Adithya Venkatadri, Lau Wayne, Lee Chwan Ren, Leong Wai Yi, Leong Wei Qi, Liew Rachel, Limkonchotiwat Peerat, Liu Bing Jie Darius, Montalan Jann Railey, Ng Boon Cheong Raymond, Ngui Jian Gang, Nguyen Thanh Ngan, Ong Brandon, Ong Tat-Wee David, Ong Zhi Hao, Rengarajan Hamsawardhini, Siow Bryan, Susanto Yosephine, Tai Ngee Chia, Tan Choon Meng, Teng Walter, Teo Eng Sipp Leslie, Teo Wei Yi, Tjhi William, Yeo Yeow Tong, Yong Xianbin
## Acknowledgements
[AI Singapore](​​https://aisingapore.org/) is a national programme supported by the National Research Foundation, Singapore and hosted by the National University of Singapore. Any opinions, findings and conclusions or recommendations expressed in this material are those of the author(s) and do not reflect the views of the National Research Foundation or the National University of Singapore. 

## Contact
For more info, please contact us using this [SEA-LION Inquiry Form](https://forms.gle/sLCUVb95wmGf43hi6)

[Link to SEA-LION's GitHub repository](https://github.com/aisingapore/sealion)

## Disclaimer
This is the repository for the commercial instruction-tuned model.
The model has _not_ been aligned for safety.
Developers and users should perform their own safety fine-tuning and related security measures.
In no event shall the authors be held liable for any claims, damages, or other liabilities arising from the use of the released weights and codes.