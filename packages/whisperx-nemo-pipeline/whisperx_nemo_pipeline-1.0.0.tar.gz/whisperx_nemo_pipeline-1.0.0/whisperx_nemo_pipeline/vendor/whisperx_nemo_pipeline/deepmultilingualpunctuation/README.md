# Deep Multilingual Punctuation Prediction

This python library predicts the punctuation of English, Italian, French and German texts. We developed it to restore the punctuation of transcribed spoken language. 

This uses [our "FullStop" model](https://huggingface.co/oliverguhr/fullstop-punctuation-multilang-large/) that we trained on the [Europarl Dataset](https://huggingface.co/datasets/wmt/europarl). *Please note that this dataset consists of political speeches. Therefore the model might perform differently on texts from other domains.*

The code restores the following punctuation markers: **"." "," "?" "-" ":"**


[Video Sample](https://user-images.githubusercontent.com/3495355/150677531-13f2037d-8673-4e34-8769-0da1784c2fe7.mp4)

## Install 

To get started install the package from [pypi](https://pypi.org/project/deepmultilingualpunctuation/):

```bash
pip install deepmultilingualpunctuation
```

## Usage
The ```PunctuationModel``` class an process texts of any length. Note that processing of very long texts can be time consuming.

### Restore Punctuation
```python
from deepmultilingualpunctuation import PunctuationModel

model = PunctuationModel()
text = "My name is Clara and I live in Berkeley California Ist das eine Frage Frau Müller"
result = model.restore_punctuation(text)
print(result)
```

**output**
> My name is Clara and I live in Berkeley, California. Ist das eine Frage, Frau Müller?


### Predict Labels 
```python
from deepmultilingualpunctuation import PunctuationModel

model = PunctuationModel()
text = "My name is Clara and I live in Berkeley California Ist das eine Frage Frau Müller"
clean_text = model.preprocess(text)
labled_words = model.predict(clean_text)
print(labled_words)
```

**output**

> [['My', '0', 0.9999887], ['name', '0', 0.99998665], ['is', '0', 0.9998579], ['Clara', '0', 0.6752215], ['and', '0', 0.99990904], ['I', '0', 0.9999877], ['live', '0', 0.9999839], ['in', '0', 0.9999515], ['Berkeley', ',', 0.99800044], ['California', '.', 0.99534047], ['Ist', '0', 0.99998784], ['das', '0', 0.99999154], ['eine', '0', 0.9999918], ['Frage', ',', 0.99622655], ['Frau', '0', 0.9999889], ['Müller', '?', 0.99863917]]

## Languages

### Models

| Languages                                  | Model                                                        |
| ------------------------------------------ | ------------------------------------------------------------ |
| English, Italian, French and German        | [oliverguhr/fullstop-punctuation-multilang-large](https://huggingface.co/oliverguhr/fullstop-punctuation-multilang-large) |
| English, Italian, French, German and Dutch | [oliverguhr/fullstop-punctuation-multilingual-sonar-base](https://huggingface.co/oliverguhr/fullstop-punctuation-multilingual-sonar-base) |
| Dutch                                      | [oliverguhr/fullstop-dutch-sonar-punctuation-prediction](https://huggingface.co/oliverguhr/fullstop-dutch-sonar-punctuation-prediction) |

### Community Models

| Languages                                  | Model                                                        |
| ------------------------------------------ | ------------------------------------------------------------ |
|English, German, French, Spanish, Bulgarian, Italian, Polish, Dutch, Czech, Portugese, Slovak, Slovenian| [kredor/punctuate-all](https://huggingface.co/kredor/punctuate-all)                                                             |
| Catalan                                    | [softcatala/fullstop-catalan-punctuation-prediction](https://huggingface.co/softcatala/fullstop-catalan-punctuation-prediction) |

You can use different models by setting the model parameter:

```python
model = PunctuationModel(model = "oliverguhr/fullstop-dutch-punctuation-prediction")
```

## Where do I find the code and can I train my own model?

Yes you can! For complete code of the reareach project take a look at [this repository](https://github.com/oliverguhr/fullstop-deep-punctuation-prediction).

There is also an guide on [how to fine tune this model for you data / language](https://github.com/oliverguhr/fullstop-deep-punctuation-prediction/blob/main/other_languages/readme.md). 


## Results 

The performance differs for the single punctuation markers as hyphens and colons, in many cases, are optional and can be substituted by either a comma or a full stop. The model achieves the following F1 scores for the different languages:

| Label         | EN    | DE    | FR    | IT    |
| ------------- | ----- | ----- | ----- | ----- |
| 0             | 0.991 | 0.997 | 0.992 | 0.989 |
| .             | 0.948 | 0.961 | 0.945 | 0.942 |
| ?             | 0.890 | 0.893 | 0.871 | 0.832 |
| ,             | 0.819 | 0.945 | 0.831 | 0.798 |
| :             | 0.575 | 0.652 | 0.620 | 0.588 |
| -             | 0.425 | 0.435 | 0.431 | 0.421 |
| macro average | 0.775 | 0.814 | 0.782 | 0.762 |



## References
Please cite us if you found this useful:

```
@article{guhr-EtAl:2021:fullstop,
  title={FullStop: Multilingual Deep Models for Punctuation Prediction},
  author    = {Guhr, Oliver  and  Schumann, Anne-Kathrin  and  Bahrmann, Frank  and  Böhme, Hans Joachim},
  booktitle      = {Proceedings of the Swiss Text Analytics Conference 2021},
  month          = {June},
  year           = {2021},
  address        = {Winterthur, Switzerland},
  publisher      = {CEUR Workshop Proceedings},  
  url       = {http://ceur-ws.org/Vol-2957/sepp_paper4.pdf}
}
```
