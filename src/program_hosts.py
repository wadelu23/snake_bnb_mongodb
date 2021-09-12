import datetime
from colorama import Fore
from dateutil import parser

from infrastructure.switchlang import switch
import infrastructure.state as state
import services.data_service as svc
from program import ensure_input_value


def run():
    print(' ****************** Welcome host **************** ')
    print()

    show_commands()

    while True:
        action = get_action()

        with switch(action) as s:
            s.case('c', create_account)
            s.case('a', log_into_account)
            s.case('l', list_cages)
            s.case('r', register_cage)
            s.case('u', update_availability)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')
            s.case(['x', 'bye', 'exit', 'exit()'], exit_app)
            s.case('?', show_commands)
            s.case('', lambda: None)
            s.default(unknown_command)

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('Login to your [a]ccount')
    print('[L]ist your cages')
    print('[R]egister a cage')
    print('[U]pdate cage availability')
    print('[V]iew your bookings')
    print('Change [M]ode (guest or host)')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def create_account():
    print(' ****************** REGISTER **************** ')
    name = input('What is your name? ')
    email = input('What is your email? ').strip().lower()

    old_account = svc.find_account_by_email(email)
    if old_account:
        error_msg(f"ERROR: Account with email {email} already exists.")
        return

    state.active_account = svc.create_account(name, email)

    success_msg(f"Created new account with id {state.active_account.id}.")


def log_into_account():
    print(' ****************** LOGIN **************** ')

    email = input('What is your email? ').strip().lower()
    account = svc.find_account_by_email(email)

    if not account:
        error_msg(f'Could not find account with email {email}.')
        return

    state.active_account = account
    success_msg('Logged in successfully.')


def register_cage():
    print(' ****************** REGISTER CAGE **************** ')

    if not state.active_account:
        error_msg(state.remind_login_msg("register a cage"))
        return

    meters = ensure_input_value(
        'How many square meters is the cage? ', type='float')
    if not meters:
        error_msg('Cancelled')
        return

    carpeted = input("Is it carpeted [y, n]? ").lower().startswith('y')
    has_toys = input("Have snake toys [y, n]? ").lower().startswith('y')
    allow_dangerous = input(
        "Can you host venomous snakes [y, n]? ").lower().startswith('y')

    name = input("Give your cage a name: ")
    if not name:
        error_msg('Cancelled')
        return

    price = ensure_input_value(
        'How much are you charging? ', type='float')
    if not price:
        error_msg('Cancelled')
        return

    cage = svc.register_cage(
        state.active_account, name,
        allow_dangerous, has_toys, carpeted,
        meters, price
    )

    state.reload_account()
    success_msg(f'Register new cage with id {cage.id}.')


def list_cages(supress_header=False):
    if not supress_header:
        print(' ******************     Your cages     **************** ')

    if not state.active_account:
        error_msg(state.remind_login_msg("view cages"))
        return

    cages = svc.find_cages_for_user(state.active_account)
    print(f"You have {len(cages)} cages.")
    for idx, c in enumerate(cages):
        print(f' {idx + 1}. {c.name} is {c.square_meters} meters.')
        for b in c.bookings:
            print('      * Booking: {}, {} days, booked? {}'.format(
                b.check_in_date,
                (b.check_out_date - b.check_in_date).days,
                'YES' if b.booked_date is not None else 'no'
            ))


def update_availability():
    print(' ****************** Add available date **************** ')

    if not state.active_account:
        error_msg(state.remind_login_msg("update date"))
        return

    list_cages(supress_header=True)

    cage_number = input("Enter cage number: ")
    if not cage_number.strip():
        error_msg('Cancelled')
        print()
        return

    cage_number = int(cage_number)

    cages = svc.find_cages_for_user(state.active_account)
    selected_cage = cages[cage_number - 1]

    success_msg("Selected cage {}".format(selected_cage.name))

    start_date = ensure_input_value(
        'Enter available date [yyyy-mm-dd]: ', type='date')
    if not start_date:
        error_msg('Cancelled')
        return

    days = ensure_input_value(
        'How many days is this block of time? ', type='int')
    if not days:
        error_msg('Cancelled')
        return

    svc.add_available_date(
        selected_cage,
        start_date,
        days
    )

    success_msg(f'Date added to cage {selected_cage.name}.')


def view_bookings():
    print(' ****************** Your bookings **************** ')

    if not state.active_account:
        error_msg(state.remind_login_msg("view bookings"))
        return

    cages = svc.find_cages_for_user(state.active_account)

    bookings = [
        (cage, booking)
        for cage in cages
        for booking in cage.bookings
        if booking.booked_date is not None
    ]

    print("You have {} bookings.".format(len(bookings)))

    for cage, booking in bookings:
        booked_date = datetime.date(
            booking.booked_date.year,
            booking.booked_date.month,
            booking.booked_date.day)
        check_in_date = datetime.date(
            booking.check_in_date.year,
            booking.check_in_date.month,
            booking.check_in_date.day)

        print(
            f' * Cage: {cage.name}, booked date: {booked_date}, from {check_in_date} for {booking.duration_in_days} days.')


def exit_app():
    print()
    print('bye')
    raise KeyboardInterrupt()


def get_action():
    text = '> '
    if state.active_account:
        text = f'{state.active_account.name}> '

    action = input(Fore.YELLOW + text + Fore.WHITE)
    return action.strip().lower()


def unknown_command():
    print("Sorry we didn't understand that command.")


def success_msg(text):
    print(Fore.LIGHTGREEN_EX + text + Fore.WHITE)


def error_msg(text):
    print(Fore.LIGHTRED_EX + text + Fore.WHITE)
