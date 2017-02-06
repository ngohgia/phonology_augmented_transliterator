#!/bin/bash
t2p_path=/data/users/ngohgia/data_drive/transliterator/utilities/t2p/t2p_dt.pl
sclite_path=/data/users/ngohgia/data_drive/transliterator/utilities/sclite/sclite

root=$(pwd)
exp_dir=$root/sample_data

main() {
  mkdir -p $exp_dir
  tag_file=$exp_dir/tags
  seq -f '(%1.f)' 6 > $tag_file
  for i in $(eval echo {1..$num_samples}); do
      work_dir=$exp_dir/work
      mkdir -p $work_dir
      train_file=$exp_dir/training.lex
      test_file=$exp_dir/test.en
      output_file=$exp_dir/test.out
      hyp_file=$exp_dir/test.hyp
      ref_file=$exp_dir/test.ref

      cd $root
      python $root/RunTransliterationWrapper.py $train_file $test_file $output_file $work_dir $t2p_path
  done
}

main
