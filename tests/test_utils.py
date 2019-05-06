from runregistry.utils import transform_to_rr_run_filter


class TestFilterCreation:
    def test_get_run(self):
        run_number = 323434
        assert transform_to_rr_run_filter(run_filter={'run_number': run_number}) == {
            'run_number': {'=': run_number}}

    def test_get_multiple_run_using_or(self):
        run_number1 = 323555
        run_number2 = 323444
        run_number3 = 343222
        run_number4 = 333333
        user_input = {
            'run_number': {
                'or': [run_number1, run_number2, run_number3, {'=': run_number4}]
            }
        }
        desired_output = {
            'run_number': {
                'or': [
                    {'=': run_number1},
                    {'=': run_number2},
                    {'=': run_number3},
                    {'=': run_number4}
                ]
            }
        }

        assert transform_to_rr_run_filter(
            run_filter=user_input) == desired_output
