# #FigTag : Find the Papers with the Data you want!

## Motivation
Often when searching for papers in [pubmed](https://www.ncbi.nlm.nih.gov/pubmed/), we are specifically looking for *papers* with __data figures which contain data related to our query__. [Open-i](https://openi.nlm.nih.gov/) is awesome, but 1) integration with pubmed would be ideal, as we are looking for papers, and that's where we normally do those searches. 2) Tagging figure with keywords, similar to MeSH for whole papers would better support finding papers with figures related to our keywords. Finally, 3) splitting up multipanel figures would likely support more fine-grained results.

1 ) is beyond the scope of the codeathon, but would cruically depend on 2) - which can leverage work already done for [Open-i](https://openi.nlm.nih.gov/) and [PMC](https://www.ncbi.nlm.nih.gov/pmc/?) to pull out figures and their legends. 3) May be able to be pursued in parallel to 2) depending on team-members' interest and skill-sets.

## Background

## Towards an Ontology of Data Figures
What high level categories of metadata might we tag figures with?
1. Source Publication
2. Figure number what, of what total number of figures
3. Subfigure identifier, if applicable
4. Chart/Graph/Figure Type
5. Grey-scale or color
6. Experiment Type from which the data was derived (the methods employed)
7. Number of replicates represented
8. The categories in which and/or axes on which data is presented
9. The materials used to perform the experiment
10. The statistical test(s) used to indicate significance, if applicable

Given a figure, the uid for its source manuscript, and the associated figure legend, we may be able to find all of these. However, it seems unlikely that we will find all of the in any one manuscript. Depending on the teams skill-set it may be more fruitful to pursue some subset of these.

## Test Data
PSGL-1 is pretty cool, and there is not TOO much data from [PMC](https://www.ncbi.nlm.nih.gov/pmc/?) indexed in [Open-i](https://openi.nlm.nih.gov/) for that keyword, so this will serve as our [test data set](https://openi.nlm.nih.gov/gridquery?q=psgl-1%20OR%20sleplg&it=u,g,c,m,mc,p,ph,x&coll=pmc&vid=1&m=1&n=100).

Information about the [Open-i](https://openi.nlm.nih.gov/) API can be found [here](https://openi.nlm.nih.gov/services?it=xg#searchAPIUsingGET).

## Requirements

please see the requirement file [here](https://github.com/NCBI-Codeathons/Automated-Figure-extraction-and-Tagging/blob/master/requirements/base.txt)

# Projects

1. Alex Kotliarov - Variational autoencoder based clustering of images
2. David Shao - Multipanel Figure Splitting
3. Ricardo V. - setting up pipeline
4. Ryan Connor, Meng Cheng, & Marie Gallagher - MeSh Indexing of Figure Legends

# Notes on MeSH Indexing of Figure Legends

The mesh indexing script may not work outside of the NLM network at the moment.

# Using Variation Autoencoder (VAE) to cluster images.

**Objective**: Learn categories of images present in publications accessible via OpenI service.

**Approach**: Given a collection of images, try to come up with a set of clusters such that each cluster represents an image category.
Therefore we are facing unsupervised learning task, where we need to perform following:

- extract relevant features that represent our samples - images
- use these features to compute similarity between samples
- cluster samples based on similarity metric.

## Training a model to extract image's features.

How do we extract features from the samples - images - and what are the features?
Let's have a neural network to find these features for us.
We will train a Variational Autoencoder model on collection of images to learn a latent Gaussian model that represents the collection of images of a training set.

Variation Autoencoder model consists of encoder, decoder and a loss function.
- Encoder is a neural network that outputs a latent representation of an image - features of an image that represent a point in the D-dimentional feature space; The encoder serves as inference model.
- Decoder is a neural network that learns to reconstruct the data - input image - given its representation (latent variables).

![Example Decoder Image Reconstruction](https://raw.githubusercontent.com/NCBI-Codeathons/Automated-Figure-extraction-and-Tagging/master/notebooks/reconstruction.png)

To train a model we
- make a decision about dimension of a feature space.
- fit model to input images to learn Gaussian distribution parameters - mu and sigma - for each feature, given the data.

Upon completion of the training process we will persist learned model as file for later use.

## Clustering model

After training a VAE model, we would use VAE model's encoder to map an input image to its latent representation - features.

We will produce features vector for each image of a training set and will use these features to fit a KMeans clustering model and decide on number of clusters using "elbow" heuristic.

We will persist learned KMeans clustering model as a file for later use.

## Assigning an image to a cluster

Given an image, we will
- Encode the image to its features vector, using pre-trained VAE encoder;
- Use ipre-trained KMeans model to predict cluster id.
- Output cluster id.

## Data sets

| Data set  | Size           |
|:----------|:--------------:|
|Training   | ~62,000 images |
|Validation | ~4,500 images  |
|Test       | ~5,000 images  |

Information

|                            |              |
|----------------------------|-------------:|
| Image size                 | 100 x 100 px |
| Dimension of feature space |          256 |
| Number of clusters         |            8 |

# Indexing images

## Setup

After checking out a local copy of the repository, please run this command:

```bash
source dev_env.sh
```

It will create a virtual environment and install all the packages that our applications need.

## Building an index

The following command will generate a SQLite DB with an index of images, the clusters they belong to per our models, a list of unique identifiers (`uid`s) of papers where the images appeared, and MeSH terms associated with them. It uses models (Variation Autoencoder and K-Means) we generated (which are stored under the `models` directory in this repository) and sample parsed MeSH terms (stored in the file `mesh_out.txt` at the root of the repository) we produced.

```bash
# Remove `-file-limit 5` to use all the files
# Remove `FIGTAG_LOGLEVEL=INFO` to not see log messages
FIGTAG_LOGLEVEL=INFO bin/figtag run \
   -query 'https://openi.nlm.nih.gov/api/search?coll=pmc&it=x%2Cu%2Cph%2Cp%2Cmc%2Cm%2Cg%2Cc&m=1&n=100&query=psgl-1%20OR%20sleplg' \
   -vae-model-file models/vae-model.256d.pt -kmeans-model-file models/kmeans_model.256d.8.pt \
   -o /tmp/`whoami`/test -file-limit 5 -mesh-terms-file mesh_out.txt
```

## Searching for figures

We provide a command line utility that allows you to search for MeSH terms in an index we can generate with the utility mentioned in the previous section. In the example below, we search for the term `Cercopithecus` using the sample index we generated before (file `samples/ImageIndex.sqlite` in this repository):

```bash
bin/figtag figure-search -query "Cercopithecus" -index samples/ImageIndex.sqlite
```

# Limitations or further improvement
1. Due to the time limitation, the integration of image processing and text mining is not completed
2. The Medical Text Indexer (MTI) tool supposed to be open to public with out requesting for credentials. However, from our test, it is available to request sent from NIH network. There may be a limited access for outside NIH users.
3. More test cases are necessary and further evaluation on the MeSH terms from FigTag project's txt mining compared with MeSH indexing could be valuable.
4. A web-based MTI API would greatly improve the efficiency of FigTag pipeline.
5. The Imagine splitter could beneit from more robust testing and tuning
6. As could the image classifier
