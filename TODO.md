# next actions


- [x] integrate Loops into Pattern
  - [ ] implement all loop operations
    - [x] xfer
      - [ ] i'd consider more carefully which order to xfer the loops in, it kinda matters for effiency of knitting
  - [ ] abstract the exceptions in the various inhooking and outhooking functions
    - [ ] seriously though these functions are awful. I'm pretty sure Prof. Danner would kill you if he saw these
  - [ ] abstract away a lot of the prelude to most of the knitting/tucking/caston functions

  - [ ] fix all the error messages but specifically the cannot infer carrier direction one. make them good instead of bad is my adivce  

  - [ ] all these functions returning knitout makes no sense
  - [ ] LOOPS NEEDS TO BE CLEANED MORE OFTEN
    - More often might not be correct but loops def are not being cleaned properly. I'm not totally sure how to fix this
  - [ ] cast on function seems right, but knits up weirdly. Not sure if the issue is the machine or the code.
    - I think this has to do with the lack of waste yarn. You could add some or do a alternating twisted tuck

# future ideas
- [ ] verbatim-mode make embedding literal knitout nicer
# integrating loops in AbstractPattern

- [ ] make a decorator that check to make sure the inputed loops are a part of all loops
- [ ] knit, miss, and xfer aren't fancy, but tuck and split make new loops
- [ ] knit, xfer, and split take loops that exist
- [ ] create request loops
- [ ] create a cast on function
- [ ] figure out how to add things to all_loops
  
