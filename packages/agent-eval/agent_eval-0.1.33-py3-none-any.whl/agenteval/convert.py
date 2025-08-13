import tempfile

# TODO: key by config pair first?
# target config name -> src config name -> split?
TASK_NAME_ALIASES = {
    "test": {
        "paper_finder_test": "PaperFindingBench",
        "paper_finder_litqa2_test": "LitQA2_FT_Search",
        "sqa_test": "ScholarQA_CS2",
        "arxivdigestables_test": "ArxivDIGESTables_Clean",
        "litqa2_test": "LitQA2_FT",
        "discoverybench_test": "DiscoveryBench",
        "core_bench_test": "CORE_Bench_Hard",
        "ds1000_test": "DS_1000",
        "e2e_discovery_test": "E2E_Bench",
        "e2e_discovery_hard_test": "E2E_Bench_Hard",
        "super_test": "SUPER_Expert",
    },
    "validation": {
        "arxivdigestables_validation": "ArxivDIGESTables_Clean",
        "sqa_dev": "ScholarQA_CS2",
        "litqa2_validation": "LitQA2_FT",
        "paper_finder_validation": "PaperFindingBench",
        "paper_finder_litqa2_validation": "LitQA2_FT_Search",
        "discoverybench_validation": "DiscoveryBench",
        "core_bench_validation": "CORE_Bench_Hard",
        "ds1000_validation": "DS_1000",
        "e2e_discovery_validation": "E2E_Bench",
        "e2e_discovery_hard_validation": "E2E_Bench_Hard",
        "super_validation": "SUPER_Expert",
    }
}


def convert_task_name(result, relevant_split, target_tasks_by_name) -> bool:
    changed_something = False

    original_task_name = result.task_name
    if original_task_name in TASK_NAME_ALIASES.get(relevant_split, {})
        new_task_name = TASK_NAME_ALIASES[relevant_split][original_task_name]
        result.task_name = new_task_name
        
    final_task_name = task_result.task_name
    if original_task_name != final_task_name:
        changed_something = True

    if final_task_name not in target_tasks_by_name:
        # TODO: probably error here?
        logger.warning(f"Unknown final task name {final_task_name}")

    return changed_something


def convert_result(result, relevant_split, src_tasks_by_name, target_tasks_by_name) -> bool:
    changed_something = False

    changed_something = changed_something or convert_task_name(
        result,
        relevant_split,
        target_tasks_by_name,
    )

    if final_task_name not in target_tasks_by_name:
        # TODO: probably error here?
        logger.warning(f"Unknown final task name {final_task_name}")
    else:
        original_primary_metric_name = src_tasks_by_name[original_task_name]
        expected_primary_metric_name = target_tasks_by_name[final_task_name]
        if original_primary_metric_name != expected_primary_metric_name:
            # # check if we can convert between the two
            # maybe_convert_to = PRIMARY_METRIC_ALIASES.get(relevant_split, {}).get(final_task_name, {}).get(original_primary_metric_name)
            # if (maybe_convert_to is not None) and (maybe_convert_to == expected_primary_metric_name):
            #     for metric in result.metrics:
            #         if metric.name == original_primary_metric_name:
            #             metric.name = expected_primary_metric_name
            #             changed_something = True
            # else:
            #     # TODO: probably error here?
            #     logger.warning(f"Cannot get to the primary metric for task {final_task_name}.")
            logger.warning(f"No primary metric for task {final_task_name}")


def convert_results(task_results, relevant_split, src_suite_config, target_tasks_by_name) -> bool:
    try:
        src_tasks_by_name = src_suite_config.get_tasks_by_name(relevant_split)
    except ValueError as exc:
        logger.warning(f"Issue getting tasks for split {relevant_split} from the source suite config.")
        # TODO: some error
        return

    # changes happen in place
    changed_something = False
    for result in task_results:
        changed_something = changed_something or convert_result(
            results=result,
            relevant_split=relevant_split,
            src_tasks_by_name=src_tasks_by_name,
            target_tasks_by_name=target_tasks_by_name,
        )
        return changed_something


def convert_lb_submission(lb_submission, target_suite_config, target_tasks_by_name) -> bool:
    changed_something = False

    # changes are made in place
    src_suite_config = lb_submission.suite_config
    changed_something = changed_something or convert_results(
        task_results=lb_submission.results,
        relevant_split=lb_submission.split,
        src_suite_config=src_suite_config,
        target_tasks_by_name=target_tasks_by_name,
    )
    if src_suite_config != target_suite_config:
        lb_submission.suite_config = target_suite_config
        changed_something = True

    return changed_something


def convert_one(
    results_repo_id: str,
    src_hf_config: str,
    split: str,
    submission_name: str,
    target_suit_config: SuiteConfig,
):
    with tempfile.TemporaryDirectory() as temp_dir:
        src_results_dir = os.path.join(temp_dir, "current")
        target_results_dir = os.path.join(temp_dir, "updated")

        local_src_filepath = hf_hub_download(
            repo_id=results_repo_id,
            filename="/".join([src_hf_config, split, submission_name, ".json"]),
            repo_type="dataset",
            local_dir=src_results_root_dir,
        )

        upload_summary_to_hf(
            api=hf_api,
            eval_result=lb_submission,
            repo_id=results_repo_id,
            config_name=hf_config,  # use the one from the args
            split=split,  # use the one from the args
            submission_name=submission_name,
        )


def get_results_inner_dir(root_results_dir: str, hf_config: str, split: str) -> str:
    return os.path.join(root_results_dir, hf_config, split)


def convert_many(
    results_repo_id: str,
    src_hf_config: str,
    split: str, 
    target_suite_config: SuiteConfig,
):
    print(f"results repo: {results_repo_id}")
    print(f"HF config: {src_hf_config}")
    print(f"split: {split}")

    try:
        target_tasks_by_name = target_suite_config.get_tasks_by_name(split)
    except ValueError as exc:
        logger.warning(f"Issue getting tasks for split {split} from the target suite config.")
        # TODO: some error

    changed_anything = False

    with tempfile.TemporaryDirectory() as temp_dir:
        src_results_root_dir = os.path.join(temp_dir, "current")
        target_results_root_dir = os.path.join(temp_dir, "updated")

        target_hf_config = target_suite_config.version
        target_results_inner_dir = get_results_inner_dir(target_results_root_dir, target_hf_config, split)
        # Some prep
        os.makedirs(target_results_inner_dir, exist_ok=True)

        snapshot_download(
            repo_id=results_repo_id,
            repo_type="dataset",
            allow_patterns=f"{src_hf_config}/{split}/*.json",
            local_dir=src_results_root_dir,
        )
        src_results_inner_dir = get_results_inner_dir(src_results_root_dir, src_hf_config, split)

        for path in os.listdir(src_results_inner_dir):
            with open(os.path.join(src_results_inner_dir, path) as f_src:
                lb_submission = LeaderboardSubmission.model_validate(json.load(f_src))

            # We can get target_tasks_by_name from target_suite_config, but pass it in
            # so we're not grabbing it for every submission
            # changes made in place
            changed_this_thing = convert_lb_submission(
                lb_submission=lb_submission,
                target_suite_config=target_suite_config,
                target_tasks_by_name=target_tasks_by_name,
            )
            changed_anything = changed_anything or changed_this_thing

            if changed_this_thing:
                with open(
                    os.path.join(target_results_inner_dir, path),
                    "w",
                    encoding="utf-8",
                ) as f_target:
                    f_target.write(lb_submission.model_dump_json(indent=None))

        if changed_anything:
            click.echo(f"Uploading converted results to {repo_id}...")
            hf_api.upload_folder(
                folder_path=target_results_root_dir,
                path_in_repo="",
                repo_id=results_repo_id,
                repo_type="dataset",
            )
