#!/bin/bash
t2p_path=/data/users/ngohgia/data_drive/transliterator/utilities/t2p/t2p_dt.pl
sclite_path=/mnt/eql/p1/users/imganalysis/ngohgia/transliterator/utilities/sclite/sclite
g2p=/data/users/minhnguyen/g2p-sequitur/lib/python/g2p.py

root=$(pwd)
exp_dir=$root/test_exp
#data_file=$root/data/randomized_short_train.lex
data_file=$root/data/randomized_training_set_g2p_form.lex
size=2000
num_samples=10

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
        #shuf $data_file > $input_file 
        mkdir -p $work_dir/corpus
        train_file=$work_dir/corpus/train.lex
        test_file=$work_dir/corpus/test.lex
        output_file=$work_dir/test.out
        hyp_file=$work_dir/test.hyp
        ref_file=$work_dir/test.ref
        #eval $make_trainset_cmd $input_file > $train_file
        #eval $make_testset_cmd $input_file | cut -f1 > $test_file
        #eval $make_testset_cmd $input_file | cut -f2 | paste -d' ' - $tag_file > $ref_file
	log_dir=$work_dir/log
	model_dir=$work_dir/g2p_model
	mkdir -p $log_dir
	mkdir -p $model_dir

        JOB=`/apps/sysapps/TORQUE/bin/qsub -l nodes=1:ppn=1,mem=50gb -V -q circ-spool<<EOJ
          #!/bin/bash
          #PBS -l walltime=48:00:00
          #PBS -l nodes=1:ppn=1
          #PBS -m ae
            cd $root

            python $g2p \
            --train $train_file \
            --devel 25% \
            --write-model $model_dir/1-gram-g2p.jsm \
            >> $log_dir/1-gram-g2p.log 2>&1

            python $g2p \
            --model $model_dir/1-gram-g2p.jsm \
            --ramp-up \
            --train $train_file \
            --devel 25% \
            --write-model $model_dir/2-gram-g2p.jsm \
            >> $log_dir/2-gram-g2p.log 2>&1
            
            python $g2p \
            --model $model_dir/2-gram-g2p.jsm \
            --ramp-up \
            --train $train_file \
            --devel 25% \
            --write-model $model_dir/3-gram-g2p.jsm \
            >> $log_dir/3-gram-g2p.log 2>&1
            
            python $g2p \
            --model $model_dir/3-gram-g2p.jsm \
            --ramp-up \
            --train $train_file \
            --devel 25% \
            --write-model $model_dir/4-gram-g2p.jsm \
            >> $log_dir/4-gram-g2p.log 2>&1
            
            python $g2p \
            --model $model_dir/4-gram-g2p.jsm \
            --ramp-up \
            --train $train_file \
            --devel 25% \
            --write-model $model_dir/5-gram-g2p.jsm \
            >> $log_dir/5-gram-g2p.log 2>&1
            
            python $g2p \
            --model $model_dir/5-gram-g2p.jsm \
            --ramp-up \
            --train $train_file \
            --devel 25% \
            --write-model $model_dir/6-gram-g2p.jsm \
            >> $log_dir/6-gram-g2p.log 2>&1
                      `
          echo "JobID = ${JOB} submitted"
    done
}
            #python $root/RunTransliterationWrapper.py $train_file $test_file $output_file $work_dir $t2p_path > /dev/null

main
