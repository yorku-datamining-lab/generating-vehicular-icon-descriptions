#!/bin/bash

# zero-shot treatements
zeroshot=(
  'gpt-4_image-and-context'
  'gpt-4_image-only'
  'gpt-4_context-only'
  'llava_image-and-context'
  'llava_image-only'
  'llava_context-only'
  'claude-3-5_image-and-context'
  'claude-3-5_image-only'
  'claude-3-5_context-only'
)

kshot=(
    'gpt-4_k-1_closest'
    'gpt-4_k-3_closest'
    'gpt-4_k-5_closest'
    'claude-3-5_k-1_closest'
    'claude-3-5_k-3_closest'
    'claude-3-5_k-5_closest'
    'llava_k-3_closest'
    'llava_k-1_closest'
    'llava_k-5_closest'
)

for model in "${zeroshot[@]}"
do
  python ../clipscore/clipscore.py "../outputs/clip/vis-input_zero-shot_$model.json"  ../outputs/icons/ --references_json "../outputs/clip/vis-ref-input_zero-shot.json" --save_per_instance "../outputs/clip/vis-output-$model.json"
  python ../clipscore/clipscore.py "../outputs/clip/fun-input_zero-shot_$model.json"  ../outputs/icons/ --references_json "../outputs/clip/fun-ref-input_zero-shot.json" --save_per_instance "../outputs/clip/fun-output-$model.json"
done

for model in "${kshot[@]}"
do
  python ../clipscore/clipscore.py "../outputs/clip/vis-input_k-shot_$model.json"  ../outputs/icons/ --references_json "../outputs/clip/vis-ref-input_k-shot.json" --save_per_instance "../outputs/clip/vis-output-$model.json"
  python ../clipscore/clipscore.py "../outputs/clip/fun-input_k-shot_$model.json"  ../outputs/icons/ --references_json "../outputs/clip/fun-ref-input_k-shot.json" --save_per_instance "../outputs/clip/fun-output-$model.json"
done