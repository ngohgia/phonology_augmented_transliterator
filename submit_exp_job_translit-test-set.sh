#!/bin/bash
t2p_path=/data/users/ngohgia/data_drive/transliterator/utilities/t2p/t2p_dt.pl
sclite_path=/mnt/eql/p1/users/imganalysis/ngohgia/transliterator/utilities/sclite/sclite

root=$(pwd)
exp_dir=$root/170607_exp_phono-aug_onc
syl_split_lex_hyp_file=$root/hcmus_syl_splitting_model/hcmus4256.txt
size=100
num_sets=1
num_iters=1

main() {
    for i in $(eval echo {1..$num_sets}); do
    for j in $(eval echo {1..$num_iters}); do
        part1=size$size
        part2=_set$i
        part3=_itr$j

        work_dir="$exp_dir/$part1/$part1$part2/$part1$part2$part3"
        run_dir=$work_dir/phono_augmented/run_on_test_dir
        log_dir=$run_dir/log
        mkdir -p $log_dir

        train_file=$work_dir/corpus/train.lex
        test_file=$work_dir/corpus/test.lex
        output_file=$run_dir/test.output

        JOB=`/apps/sysapps/TORQUE/bin/qsub -l nodes=1:ppn=1,mem=10gb -V -q circ-spool<<EOJ
          #!/bin/bash
          #PBS -l walltime=48:00:00
          #PBS -l nodes=1:ppn=1
          #PBS -e "${log_dir}/err_${JOB}.txt"
          #PBS -o "${log_dir}/out_${JOB}.txt"
          #PBS -m ae
            cd $root
            python $root/RunTransliterationWrapper_singleLang.py $train_file $test_file $syl_split_lex_hyp_file $output_file $run_dir $t2p_path
          `
          echo "JobID = ${JOB} submitted"
    done
    done
}

main
