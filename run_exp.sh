#!/bin/bash
t2p_path=~/srproject/t2p/t2p_dt.pl
g2p=g2p.py

root=$(pwd)
exp_dir=$root/test_exp
data_file=$root/data/randomized_short_train.lex
size=1000

main() {
	_s=$(($size/5))
	make_testset_cmd=$(echo "sed -n '1,$(($_s))p; $(($_s+1))q'")
	make_trainset_cmd=$(echo "sed -n '$(($_s+1)),$(($size))p; $(($size+1))q'")
    tag_file=$exp_dir/tags
    cat /dev/null > $tag_file
    for i in $(eval echo {1..$_s}); do
        echo "($i)" >> $tag_file
    done
    for i in {1..5}; do
        part1=size$size
        part2=_iter$i
        work_dir="$exp_dir/$part1$part2"
        mkdir -p $work_dir 
        input_file="$work_dir/input.lex"
        # shuf $data_file > $input_file 
        mkdir -p $work_dir/corpus
        train_file=$work_dir/corpus/train.lex
        test_file=$work_dir/corpus/test.lex
        output_file=$work_dir/test.out
        hyp_file=$work_dir/test.hyp
        ref_file=$work_dir/test.ref
        eval $make_trainset_cmd $input_file > $train_file
        eval $make_testset_cmd $input_file | cut -f1 > $test_file
        eval $make_testset_cmd $input_file | cut -f2 | paste -d' ' - $tag_file > $ref_file
        python $root/RunTransliterationWrapper.py $train_file $test_file $output_file $work_dir $t2p_path | tee $work_dir/full_log

        # run_g2p_experiment 6 $work_dir

        paste -d' ' $output_file $tag_file > $hyp_file
        cd $work_dir
        sclite -h $hyp_file -r $ref_file -i wsj -o dtl -n report > /dev/null
        line=$part1$part2
        echo $(pwd)
        line+=,`grep 'Total Error' report.dtl | tr -s " " | cut -d' ' -f5 | tr -d "%"`
        line+=,`grep 'with errors' report.dtl | tr -s " " | cut -d' ' -f4 | tr -d "%"`
        cd $root
        echo $line >> "${exp_dir}/report.csv"

        echo "Finish size $size, $i run"
    done
}

#Usage run_experiment $ORDER $DIR
run_g2p_experiment() {
    corpus=$2/corpus
    train_file=$corpus/train.lex
    test_file=$corpus/test.lex
    ref_file=$2/test.ref

    log_dir=$2/log
    model_dir=$2/g2p_model
    mkdir -p $log_dir
    mkdir -p $model_dir

    tag_file=$2/tags
    cat /dev/null > $tag_file
    for i in $(eval echo {1..$_s}); do
        echo "($i)" >> $tag_file
    done

    line="g2p $part1$part2"
    for M in $(eval echo {1..$1}) ; do
        if [ $M -gt 1 ] ; then
            init="
            --model $model_dir/$(($M - 1))-gram-g2p.jsm
            --ramp-up
            "
        else
            init=""
        fi

        $g2p $init \
        --train $train_file \
        --devel 25% \
        --write-model $model_dir/$M-gram-g2p.jsm \
        >> $log_dir/$M-gram-g2p.log 2>&1
	
        output_file=$2/$M-gram_g2p.out
        hyp_file=$2/$M-gram_g2p.hyp

		$g2p \
	    --model $model_dir/$M-gram-g2p.jsm \
	    --apply $test_file \
        > $output_file

        report_name=$M-gram_report
        report_file=$2/$M-gram_report.dtl

        cut -f2- $output_file | paste -d' ' - $tag_file > $hyp_file
        sclite -h $hyp_file -r $ref_file -i wsj -o dtl -n $report_name > /dev/null

        line+=,`grep 'Total Error' $report_file | tr -s " " | cut -d' ' -f5 | tr -d "%"`
        line+=,`grep 'with errors' $report_file | tr -s " " | cut -d' ' -f4 | tr -d "%"`
        echo "Finish $M-gram-g2p"
    done

    echo $line >> report.csv
}

main
