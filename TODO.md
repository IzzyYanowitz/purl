# next actions


- [ ] integrate Loops into AbstractPattern
  - [ ] implement all loop operations
    - [x] knit
    - [x] miss
    - [x] tuck
    - [x] split
    - [x] xfer
      - [ ] i'd consider more carefully which order to xfer the loops in, it kinda matters
    - [x] 
request loops
    - [x] request needles
  - [ ] figure out how to handle Loops.split creating new loops
  - [ ] abstract the exceptions in the various inhooking and outhooking functions
    - [ ] seriously though these functions are awful. I'm pretty sure Prof. Danner would kill you if he saw these
  - [ ] abstract away a lot of the prelude to most of the knitting/tucking/caston functions
  - [ ] consider if should be able to outhook a carrier that was never inhooked

  - [ ] fix all the error messages but specifically the cannot infer carrier direction one. make them good instead of bad is my adivce  

  - [ ] all these functions returning knitout makes no sense
  - [ ] 
# dumping program
- [ ] dump all ideas into here and organize them


# future ideas
- [ ] verbatim-mode figure out how to embed literal knitout
# integrating loops in AbstractPattern

- [ ] make a decorator that check to make sure the inputed loops are a part of all loops
- [ ] knit, miss, and xfer aren't fancy, but tuck and split make new loops
- [ ] knit, xfer, and split take loops that exist
- [ ] create request loops
- [ ] create a cast on function
- [ ] figure out how to add things to all_loops
 