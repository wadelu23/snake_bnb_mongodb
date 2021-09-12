import datetime
from dateutil import parser

from infrastructure.switchlang import switch
import program_hosts as hosts
import services.data_service as svc
from program_hosts import success_msg, error_msg
from program import ensure_input_value
import infrastructure.state as state


def run():
    print(' ****************** Welcome guest **************** ')
    print()

    show_commands()

    while True:
        action = hosts.get_action()

        with switch(action) as s:
            s.case('c', hosts.create_account)
            s.case('l', hosts.log_into_account)

            s.case('a', add_a_snake)
            s.case('y', view_your_snakes)
            s.case('b', book_a_cage)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')

            s.case('?', show_commands)
            s.case('', lambda: None)
            s.case(['x', 'bye', 'exit', 'exit()'], hosts.exit_app)

            s.default(hosts.unknown_command)

        state.reload_account()

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('[L]ogin to your account')
    print('[B]ook a cage')
    print('[A]dd a snake')
    print('View [y]our snakes')
    print('[V]iew your bookings')
    print('[M]ain menu')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def add_a_snake():
    print(' ****************** Add a snake **************** ')
    if not state.active_account:
        error_msg(state.remind_login_msg("add a snake"))
        return

    name = input("What is your snake's name? ")
    if not name:
        error_msg('cancelled')
        return

    text = 'How long is your snake (in meters)? '
    length = ensure_input_value(text, type='float')
    if not length:
        error_msg('cancelled')
        return

    species = input("Species? ")
    is_venomous = input(
        "Is your snake venomous [y]es, [n]o? ").lower().startswith('y')

    snake = svc.add_snake(state.active_account, name,
                          length, species, is_venomous)
    state.reload_account()
    success_msg('Created {} with id {}'.format(snake.name, snake.id))


def view_your_snakes():
    print(' ****************** Your snakes **************** ')
    if not state.active_account:
        error_msg(state.remind_login_msg("view your snakes"))
        return

    snakes = svc.get_snakes_for_user(state.active_account.id)
    print("You have {} snakes.".format(len(snakes)))
    for s in snakes:
        print(" * {} is a {} that is {}m long and is {}venomous.".format(
            s.name,
            s.species,
            s.length,
            '' if s.is_venomous else 'not '
        ))


def book_a_cage():
    print(' ****************** Book a cage **************** ')
    if not state.active_account:
        error_msg(state.remind_login_msg("book a cage"))
        return

    snakes = svc.get_snakes_for_user(state.active_account.id)
    if not snakes:
        error_msg('You must first [a]dd a snake before you can book a cage.')
        return

    print("Let's start by finding available cages.")
    ask_check_in_text = "Check-in date [yyyy-mm-dd]: "
    checkin = ensure_input_value(ask_check_in_text, type='date')
    if not checkin:
        error_msg('cancelled')
        return

    check_in_ahead_days = 6
    now = datetime.datetime.now()
    while (checkin - now).days < check_in_ahead_days:
        print("Notice: only ahead 7 days ")
        checkin = ensure_input_value(ask_check_in_text, type='date')
        if not checkin:
            error_msg('cancelled')
            return

    checkout = ensure_input_value("Check-out date [yyyy-mm-dd]: ", type='date')
    if not checkout:
        error_msg('cancelled')
        return

    if checkin >= checkout:
        error_msg('Check in must be before check out')
        return

    print()
    for idx, s in enumerate(snakes):
        print('{}. {} (length: {}, venomous: {})'.format(
            idx + 1,
            s.name,
            s.length,
            'yes' if s.is_venomous else 'no'
        ))

    snake = snakes[int(input('Which snake do you want to book (number)')) - 1]

    cages = svc.get_available_cages(checkin, checkout, snake)

    print("There are {} cages available in that time.".format(len(cages)))
    for idx, c in enumerate(cages):
        print(" {}. {} with {}m carpeted: {}, has toys: {}.".format(
            idx + 1,
            c.name,
            c.square_meters,
            'yes' if c.is_carpeted else 'no',
            'yes' if c.has_toys else 'no'))

    if not cages:
        error_msg("Sorry, no cages are available for that date.")
        return

    cage = cages[int(input('Which cage do you want to book (number)')) - 1]
    svc.book_cage(state.active_account, snake, cage, checkin, checkout)

    success_msg(
        'Successfully booked {} for {} at ${}/night.'.format(cage.name, snake.name, cage.price))


def view_bookings():
    print(' ****************** Your bookings **************** ')
    if not state.active_account:
        error_msg(state.remind_login_msg("view your bookings"))
        return

    snakes = {s.id: s for s in svc.get_snakes_for_user(
        state.active_account.id)}

    bookings = svc.get_bookings_for_user(state.active_account.email)

    print(f'You have {len(bookings)} bookings.')
    for b in bookings:
        snake_name = snakes.get(b.guest_snake_id).name
        check_in_date = datetime.date(
            b.check_in_date.year,
            b.check_in_date.month,
            b.check_in_date.day)
        booked_days = (b.check_out_date - b.check_in_date).days

        print(
            f'* Snake: {snake_name} is booked at {b.cage.name} from {check_in_date} for {booked_days} days.')
