# Automated-Figure-extraction-and-Tagging

## Motivation
Often when searching for papers in [pubmed](https://www.ncbi.nlm.nih.gov/pubmed/), we are specifically looking for *papers* with __data figures which contain data related to our query__. [Open-i](https://openi.nlm.nih.gov/) is awesome, but 1) integration with pubmed would be ideal, as we are looking for papers, and that's where we normally do those searches. 2) Tagging figure with keywords, similar to MeSH for whole papers would better support finding papers with figures related to our keywords. Finally, 3) splitting up multipanel figures would likely support more fine-grained results.

1 ) is beyond the scope of the codeathon, but would cruically depend on 2) - which can leverage work already done for [Open-i](https://openi.nlm.nih.gov/) and [PMC](https://www.ncbi.nlm.nih.gov/pmc/?) to pull out figures and their legends. 3) May be able to be pursued in parallel to 2) depending on team-members' interest and skill-sets.

## Background

### Towards an Ontology of Data Figures
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

### Test Data
PSGL-1 is pretty cool, and there is not TOO much data from [PMC](https://www.ncbi.nlm.nih.gov/pmc/?) indexed in [Open-i](https://openi.nlm.nih.gov/) for that keyword, so this will serve as our [test data set](https://openi.nlm.nih.gov/gridquery?q=psgl-1%20OR%20sleplg&it=u,g,c,m,mc,p,ph,x&coll=pmc&vid=1&m=1&n=100).

Information about the [Open-i](https://openi.nlm.nih.gov/) API can be found [here](https://openi.nlm.nih.gov/services?it=xg#searchAPIUsingGET).

# Projects

1. Alex Kotliarov - Variational autoencoder based classification of images
2. David Shao & Ricardo Villamarin - Multipanel Figure Splitting
3. Ryan Connor, Meng Cheng, & Marie Gallagher - MeSh Indexing of Figure Legends
