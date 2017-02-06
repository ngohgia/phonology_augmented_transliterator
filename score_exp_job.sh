#!/bin/bash
t2p_path=/data/users/ngohgia/data_drive/transliterator/utilities/t2p/t2p_dt.pl
sclite_path=/mnt/eql/p1/users/imganalysis/ngohgia/transliterator/utilities/sclite/sclite
g2p=g2p.py

root=$(pwd)
exp_dir=$root/exp_20160829
#data_file=$root/data/randomized_short_train.lex
data_file=$root/data/randomized_training_set_g2p_form.lex
size=1000
num_samples=10
report_file=$root/report-`date +%m%d`.csv

main() {
	_s=$(($size/5))
	make_testset_cmd=$(echo "sed -n '1,$(($_s))p; $(($_s+1))q'")
	make_trainset_cmd=$(echo "sed -n '$(($_s+1)),$(($size))p; $(($size+1))q'")
    tag_file=$exp_dir/tags
    cat /dev/null > $tag_file
    for i in $(eval echo {1..$_s}); do
        echo "($i)" >> $tag_file
    done
    for i in $(eval echo {1..$num_samples}); do
        part1=size$size
        part2=_iter$i
        work_dir="$exp_dir/$part1$part2"
        mkdir -p $work_dir 
        input_file="$work_dir/input.lex"
        mkdir -p $work_dir/corpus
        train_file=$work_dir/corpus/train.lex
        test_file=$work_dir/corpus/test.lex
        output_file=$work_dir/test.out
        hyp_file=$work_dir/test.hyp
        ref_file=$work_dir/test.ref

	paste -d' ' $output_file $tag_file > $hyp_file
	cd $work_dir
	$sclite_path -h $hyp_file -r $ref_file -i wsj -o dtl -n report > /dev/null

	echo $(pwd)
        line=$part1$part2
	line+=,`grep 'Total Error' report.dtl | tr -s " " | cut -d' ' -f5 | tr -d "%"`
	line+=,`grep 'with errors' report.dtl | tr -s " " | cut -d' ' -f4 | tr -d "%"`
        echo $line >> $report_file
	echo "Finish size $size, $i run"

	cd $root
    done
}

main
