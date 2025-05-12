# SDA
## data_collect
version: python==3.9  tree-sitter==0.20.1
1.run git_clone.py: Crawl the project from git
2.run dataCrawlOut.py :Analyze the commit data to obtain the diff and the C files before and after
3.run diff_func.py : Convert the key of josn
4.run git_diff.py: To obtain the diff information, remember to change the Authorization
5.run git_func.py: Obtain the func_after information

## scene_dependency_model
version: python==3.12 cuda==12.4 numpy==1.26.4 tqdm==4.66.4 tranformers==4.49.0
1.run patch_before.py, Generate the sav file using pdbert
2.The Patch is refined again using the generated sav file.
3. Message_classifier uses robert to generate sav files.
4. join_result generates the final result.

## evaluation
version: python==3.12 cuda==12.4 numpy==1.26.4 tqdm==4.66.4 tranformers==4.49.0
1. git clone https://github.com/DLVulDet/PrimeVul.git
2. PROJECT="primevul_cls"
TYPE="codet5"
MODEL="codet5-base"
TOKENIZER="codet5-base"
OUTPUT_DIR=../output/	

3.python run_ft.py \
    --project ${PROJECT} \
    --model_dir ${MODEL} \
    --output_dir=${OUTPUT_DIR} \
    --model_type=${TYPE} \
    --tokenizer_name=${TOKENIZER} \
    --model_name_or_path=${MODEL} \
    --do_train \
    --do_test \
    --train_data_file=../data/primevul_train.jsonl \
    --eval_data_file=../data/primevul_valid.jsonl \
    --test_data_file=../data/primevul_test.jsonl \
    --epoch 10 \
    --block_size 512 \
    --train_batch_size 16 \
    --eval_batch_size 16 \
    --learning_rate 2e-5 \
    --warmup_steps 1000 \
    --max_grad_norm 1.0 \
    --evaluate_during_training \
    --seed 123456


