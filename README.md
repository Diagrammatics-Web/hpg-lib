# Hourglass-Plabic-Graphs


## Useful links

- "Webs in degree two from hourglass plabic graphs" -- https://arxiv.org/abs/2402.13978
- "Rotation-invariant web bases from hourglass plabic graphs" -- https://arxiv.org/abs/2306.12501
- "Promotion permutations for tableaux" -- https://arxiv.org/abs/2306.12506

## Software Engineering / misc.
- [x] fix vertex label enter, update, exit structure to be more concise
    - can probably just use `.join()`
- [x] fix connectedness issue with the face rendering
- [x] maintain `selected` status of vertices as we move them on canvas. This requires maintaining `selected` state as we pass data between frontend/backend
- [x] fix port overlap issue
- [x] fix in-notebook rendering issues
- [x] fix 'New' button so it works inside the notebook
- [x] Eel has trouble handling multiple instances of the app object instantiated
    - solve this by: making one webserver in hourglass module, but when we can instantiate as many apps as we want
    - need to read into this more: in particular, how to restart an eel server after closed
    - this may have to do with the overlap between exposed functions — i.e. we may need to completely separate the exposure of functions from the inner workings of the graph object, and make the exposed functions universal.
        - single app object in hourglass module can handle exposing functions, and the source of information comes from whichever graph object is "current"

## Relevant TODOs
Large list of tasks in progress and to start:
- [x] ability to maintain multiple trip permutations
- [x] separate analyze and edit modes, possibly begin structuring functionality for modes to be added in future
- [x] faces
- [x] benzene move on faces
- [x] square move on faces
    - refer to [fig2](/imgs/fig2.png)
- [x] snap vertices to boundary
- [x] fix vertex selection so elements added to selected arrays on both clicking and dragging, but if dragged, deselected on release
- [ ] force layout?
- [ ] benzene and square move equivalence methods
    - [ ] benzene move
    - [ ] square move
- [ ] algorithm for applying rules to the linear order style and converting to a circular style of graph
- *[ ] conversion routine from stacked box picture to graph
- [ ] conversion from alternating sign matrices (these matrices and plane partitions are already implemented in sage)
- *[ ] translation from conventional plabic graph
- *[ ] proper labelings
    - s.t. around each internal vertex, the numbers 1-4 appear once each
    - this is already implemented in Dr. Swanson’s research code for smaller webs
- *[ ] tagging vertices with edge starting point
- [x] ability to get dual graph
- *[ ] permutations of the boundary vertices — trouble is this model is very unstructured, so may not be interesting enough to warrant implementing
- *[ ] symmetrized six-vertex pictures: convert to plabic, partial convert from plabic in contracted case
- *[ ] Chris Fraser 2-column case
- *[ ] uncrossing rules, other reduction rules, formal sums of webs
- *[ ] separation labeling

## Ordering of TODOs
4. [ ] Cayley transform from circular graph to graph with flat "boundary"
5. [ ] algorithm for applying rules to the linear order style and converting to a circular style of graph
6. [ ] conversion from alternating sign matrics
7. [ ] conversion from plane partitions


## Random thoughts
- [ ] making sure a user cannot add an edge twice
- [ ] easy rotation of graph canvas
