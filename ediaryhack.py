import argparse
from random import choices
import os
import sys

import django
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from datacenter.models import Chastisement, Commendation, Lesson, Schoolkid, Subject, Mark

commendations = [
    'Молодец!',
    'Отлично!',
    'Хорошо!',
    'Гораздо лучше, чем я ожидал!',
    'Ты меня приятно удивил!',
    'Великолепно!',
    'Прекрасно!',
    'Ты меня очень обрадовал!',
    'Именно этого я давно ждал от тебя!',
    'Сказано здорово – просто и ясно!',
    'Ты, как всегда, точен!',
    'Очень хороший ответ!',
    'Талантливо!',
    'Ты сегодня прыгнул выше головы!',
    'Я поражен!',
    'Уже существенно лучше!',
    'Потрясающе!',
    'Замечательно!',
    'Прекрасное начало!',
    'Так держать!',
    'Ты на верном пути!',
    'Здорово!',
    'Это как раз то, что нужно!',
    'Я тобой горжусь!',
    'С каждым разом у тебя получается всё лучше!',
    'Мы с тобой не зря поработали!',
    'Я вижу, как ты стараешься!',
    'Ты растешь над собой!',
    'Ты многое сделал, я это вижу!',
    'Теперь у тебя точно все получится!',
    'Я в восхищении!'
]


def get_schoolkid(kid_name):
    try:
        return Schoolkid.objects.get(full_name__contains=kid_name)
    except MultipleObjectsReturned as e1:
        print(f'Найдено несколько учеников "{kid_name}"! Укажите более точное ФИО.')
        return
    except ObjectDoesNotExist as e2:
        print(f'Ученик "{kid_name}" не найден!')
        return


def fix_marks(kid_name):
    kid = get_schoolkid(kid_name)
    if kid:
        bad_points = Mark.objects.filter(schoolkid=kid, points__lt=4)
        bad_points.update(points=5)


def create_commendation(kid_name, subject_name):
    kid = get_schoolkid(kid_name)
    if kid:
        try:
            subject = Subject.objects.get(title=subject_name, year_of_study=kid.year_of_study)
        except ObjectDoesNotExist:
            print(f'Ошибка! Предмет "{subject_name}" не найден.')
            return

        lesson = Lesson.objects.filter(year_of_study=kid.year_of_study, group_letter=kid.group_letter,
                                       subject__title=subject_name).order_by('-date')[0]
        Commendation(text=choices(commendations)[0], created=lesson.date,
                     schoolkid=kid, subject=subject, teacher=lesson.teacher).save()


def remove_chastisements(kid_name):
    kid = get_schoolkid(kid_name)
    if kid:
        Chastisement.objects.filter(schoolkid=kid).delete()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='EDiary bad data corrector',
        description='''Программа для исправления данных в электронном дневнике ученика:
замена всех плохих оценок на пятёрки; удаление замечаний учителей; создание похвалы от учителя''',
        epilog='''Автор не несёт никакой ответственности за последствия корректировок эл.дневника!!!
Все изменения вы делаете на свой страх и риск!!!
(C) redbor24''',
        add_help=False
    )
    subparser = parser.add_subparsers(
        dest='method',
        title='Допустимые команды',
        description='Команды, передаваемые первым параметром'
    )

    parent_group = parser.add_argument_group(title='Параметры')
    parent_group.add_argument('--help', '-h', action='help', help='Справка по параметрам запуска')

    parser_create_commend = subparser.add_parser(
        'create_commend',
        add_help=False,
        help='Запуск в режиме "Создание похвалы от учителя"',
        description='''Запуск в режиме "Создание похвалы от учителя".
В этом режиме программа создаёт ученику похвалу от учителя со случайным текстом.''')
    create_commend_group = parser_create_commend.add_argument_group(title='Параметры')
    create_commend_group.add_argument('--help', '-h', action='help', help='Справка')
    create_commend_group.add_argument(
        'kid',
        help='ФИО ученика. Раздельные имя, отчество и фамилия нужно взять в двойные кавычки. Регистр важен!')
    create_commend_group.add_argument('subject', help='Наименование предмета с большой буквы')

    parser_remove_chast = subparser.add_parser(
        'remove_chast',
        add_help=False,
        help='Запуск в режиме "Удаление замечаний от учителей"',
        description='''Запуск в режиме "Удаление замечаний от учителей".
В этом режиме программа удаляет у ученика все замечания от учителей.''')
    remove_chast_group = parser_remove_chast.add_argument_group(title='Параметры')
    remove_chast_group.add_argument('--help', '-h', action='help', help='Справка')
    remove_chast_group.add_argument(
        'kid',
        help='ФИО ученика. Раздельные имя, отчество и фамилия нужно взять в двойные кавычки. Регистр важен!')

    parser_fix_marks = subparser.add_parser(
        'fix_marks',
        add_help=False,
        help='Запуск в режиме "Замена плохих оценок на пятёрки"',
        description='''Запуск в режиме "Замена плохих оценок на пятёрки".
В этом режиме программа заменяет ученику на пятёрки все оценки ниже четвёрки.''')
    fix_marks_group = parser_fix_marks.add_argument_group(title='Параметры')
    fix_marks_group.add_argument('--help', '-h', action='help', help='Справка')
    fix_marks_group.add_argument(
        'kid',
        help='ФИО ученика. Раздельные имя, отчество и фамилия нужно взять в двойные кавычки. Регистр важен!')

    namespace = parser.parse_args(sys.argv[1:])

    if namespace.method == 'create_commend':
        create_commendation(namespace.kid, namespace.subject)
    elif namespace.method == 'remove_chast':
        remove_chastisements(namespace.kid)
    elif namespace.method == 'fix_marks':
        fix_marks(namespace.kid)
    else:
        parser.print_help()
