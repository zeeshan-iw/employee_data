
def post_init_hook(env):
    env["hr.employee"]._install_employee_firstname()
