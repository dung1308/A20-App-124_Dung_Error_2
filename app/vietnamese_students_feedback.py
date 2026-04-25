# coding=utf-8
# Copyright 2020 The HuggingFace Datasets Authors and the current dataset script contributor.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Vietnamese Students’ Feedback Corpus."""

import datasets


_CITATION = """\
@InProceedings{8573337,
  author={Nguyen, Kiet Van and Nguyen, Vu Duc and Nguyen, Phu X. V. and Truong, Tham T. H. and Nguyen, Ngan Luu-Thuy},
  booktitle={2018 10th International Conference on Knowledge and Systems Engineering (KSE)},
  title={UIT-VSFC: Vietnamese Students’ Feedback Corpus for Sentiment Analysis},
  year={2018},
  volume={},
  number={},
  pages={19-24},
  doi={10.1109/KSE.2018.8573337}
}
"""

_DESCRIPTION = """\
Students’ feedback is a vital resource for the interdisciplinary research involving the combining of two different
research fields between sentiment analysis and education.

Vietnamese Students’ Feedback Corpus (UIT-VSFC) is the resource consists of over 16,000 sentences which are
human-annotated with two different tasks: sentiment-based and topic-based classifications.

To assess the quality of our corpus, we measure the annotator agreements and classification evaluation on the
UIT-VSFC corpus. As a result, we obtained the inter-annotator agreement of sentiments and topics with more than over
91% and 71% respectively. In addition, we built the baseline model with the Maximum Entropy classifier and achieved
approximately 88% of the sentiment F1-score and over 84% of the topic F1-score.
"""

_HOMEPAGE = "https://sites.google.com/uit.edu.vn/uit-nlp/datasets-projects#h.p_4Brw8L-cbfTe"

# TODO: Add the licence for the dataset here if you can find it
# _LICENSE = ""

_URLS = {
    datasets.Split.TRAIN: {
        "sentences": "https://drive.google.com/uc?id=1nzak5OkrheRV1ltOGCXkT671bmjODLhP&export=download",
        "sentiments": "https://drive.google.com/uc?id=1ye-gOZIBqXdKOoi_YxvpT6FeRNmViPPv&export=down load",
        "topics": "https://drive.google.com/uc?id=14MuDtwMnNOcr4z_8KdpxprjbwaQ7lJ_C&export=download",
    },
    datasets.Split.VALIDATION: {
        "sentences": "https://drive.google.com/uc?id=1sMJSR3oRfPc3fe1gK-V3W5F24tov_517&export=download",
        "sentiments": "https://drive.google.com/uc?id=1GiY1AOp41dLXIIkgES4422AuDwmbUseL&export=download",
        "topics": "https://drive.google.com/uc?id=1DwLgDEaFWQe8mOd7EpF-xqMEbDLfdT-W&export=download",
    },
    datasets.Split.TEST: {
        "sentences": "https://drive.google.com/uc?id=1aNMOeZZbNwSRkjyCWAGtNCMa3YrshR-n&export=download",
        "sentiments": "https://drive.google.com/uc?id=1vkQS5gI0is4ACU58-AbWusnemw7KZNfO&export=download",
        "topics": "https://drive.google.com/uc?id=1_ArMpDguVsbUGl-xSMkTF_p5KpZrmpSB&export=download",
    },
}


class VietnameseStudentsFeedback(datasets.GeneratorBasedBuilder):
    """Vietnamese Students’ Feedback Corpus."""

    VERSION = datasets.Version("1.0.0")

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features(
                {
                    "sentence": datasets.Value("string"),
                    "sentiment": datasets.ClassLabel(names=["negative", "neutral", "positive"]),
                    "topic": datasets.ClassLabel(names=["lecturer", "training_program", "facility", "others"]),
                }
            ),
            homepage=_HOMEPAGE,
            # license=_LICENSE,
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        data_dir = dl_manager.download(_URLS)
        return [
            datasets.SplitGenerator(
                name=split,
                gen_kwargs={
                    "sentences_path": data_dir[split]["sentences"],
                    "sentiments_path": data_dir[split]["sentiments"],
                    "topics_path": data_dir[split]["topics"],
                },
            ) for split in _URLS
        ]

    def _generate_examples(self, sentences_path, sentiments_path, topics_path):
        with open(sentences_path, encoding="utf-8") as sentences, open(
            sentiments_path, encoding="utf-8"
        ) as sentiments, open(topics_path, encoding="utf-8") as topics:
            for key, (sentence, sentiment, topic) in enumerate(zip(sentences, sentiments, topics)):
                yield key, {
                    "sentence": sentence.strip(),
                    "sentiment": int(sentiment.strip()),
                    "topic": int(topic.strip()),
                }
