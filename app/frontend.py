
from nicegui import ui

import requests

from .functions import do_login,list_tasks,sign_up


@ui.page('/')
def home():
    with ui.row().classes("min-h-screen justify-center items-center bg-gray-50"):
        with ui.column().classes("space-y-6 items-center"):
            
            ui.label('📋 Task Manager App').classes(
                "text-4xl font-extrabold text-gray-800 text-center"
            )
            
            ui.label('Organize your tasks efficiently and never miss a deadline!').classes(
                "text-gray-600 text-center text-lg max-w-xl"
            )
            
            with ui.row().classes("space-x-4"):
                ui.button('Login', on_click=lambda: ui.navigate.to('/login')).classes(
                    "bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl text-lg shadow-md"
                )
                ui.button('Sign Up', on_click=lambda: ui.navigate.to('/signup')).classes(
                    "bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-xl text-lg shadow-md"
                )


@ui.page('/login')
def login_page():
    with ui.column().classes('w-full h-screen items-center justify-center bg-gray-100'):
        with ui.card().classes('w-96 p-6 shadow-lg rounded-xl'):
            ui.label('🔑 Login').classes("text-2xl font-bold")
            user = ui.input("Username").props("outlined clearable").classes("w-full mb-3")
            password = ui.input("Password", password=True, password_toggle_button=True).props("outlined").classes("w-full mb-3")
            ui.button('Login', on_click=lambda: do_login(user.value, password.value)).classes("w-full bg-gray-200 mt-2")
            ui.label("Does not have an account?").classes("mt-4 text-center text-gray-500")
            ui.button("creat account",on_click=lambda:ui.navigate.to('/signup')).classes("w-full bg-gray-200 hover:bg-gray-300 mt-2")


@ui.page('/signup')
def signup_page():
    with ui.column().classes('w-full h-screen items-center justify-center bg-gray-100'):
        with ui.card().classes('w-96 p-6 shadow-lg rounded-xl'):
            ui.label('📝 Sign Up').classes("text-2xl font-bold text-center mb-4")
            username = ui.input("Username").props("outlined clearable").classes("w-full mb-3")
            password = ui.input("Password", password=True, password_toggle_button=True).props("outlined").classes("w-full mb-3")
            ui.button('Creat account', on_click=lambda: sign_up(username.value, password.value)).classes("w-full bg-green-500 text-white")
            ui.label("Already have an account?").classes("mt-4 text-center text-gray-500")
            ui.button("Login", on_click=lambda: ui.navigate.to('/login')).classes("w-full bg-gray-200 mt-2")

@ui.page('/dashboard')
def dashboard():
    
    list_tasks(task_area = ui.column().classes("w-full"))


def runfrontend(**kwargs):
    ui.run(**kwargs)







        

