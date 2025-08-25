from nicegui import ui
import requests
import datetime
from dateutil import parser
from typing import Optional, Dict, Any
import json
from .db.models import priorityEnum

token = None
current_user = None

def handle_api_response(response: requests.Response, success_message: str = None) -> Dict[Any, Any]:
    try:
        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
        else:
            data = {"detail": response.text}
    except json.JSONDecodeError:
        data = {"detail": "Invalid response format"}
    
    if response.status_code in (200, 201):
        if success_message:
            ui.notify(success_message, color="green")
        return data
    else:
        error_message = data.get("detail", f"Request failed with status {response.status_code}")
        ui.notify(error_message, color="red")
        print(error_message)
        return {}

def get_priority_display(priority: str) -> Dict[str, str]:
    priority_lower = priority.lower()
    
    priority_config = {
        'high': {
            'color': 'text-red-600',
            'bg_color': 'bg-red-100',
            'border_color': 'border-red-200',
            'icon': '⚡',
            'badge_class': 'bg-red-500 text-white'
        },
        'medium': {
            'color': 'text-yellow-600', 
            'bg_color': 'bg-yellow-100',
            'border_color': 'border-yellow-200',
            'icon': '⚠️',
            'badge_class': 'bg-yellow-500 text-white'
        },
        'low': {
            'color': 'text-green-600',
            'bg_color': 'bg-green-100', 
            'border_color': 'border-green-200',
            'icon': '📝',
            'badge_class': 'bg-green-500 text-white'
        }
    }
    
    return priority_config.get(priority_lower, priority_config['low'])

def do_login(username: str, password: str):
    global token, current_user
    
    if not username.strip() or not password.strip():
        ui.notify("Please enter both username and password", color="red")
        return
    
    try:
        response = requests.post(
            "http://localhost:8000/login", 
            data={"username": username.strip(), "password": password}
        )
        
        user_data = handle_api_response(response)
        
        if "access_token" in user_data:
            token = user_data["access_token"]
            current_user = user_data.get("username", username)
            ui.notify("✅ Login successful!", color="green")
            ui.navigate.to("/dashboard")
        else:
            ui.notify("❌ Invalid credentials", color="red")
            
    except requests.RequestException as e:
        ui.notify(f"❌ Connection error: {str(e)}", color="red")
        print(f"Login error: {e}")

def sign_up(username: str, password: str):
    if not username.strip() or not password.strip():
        ui.notify("Please enter both username and password", color="red")
        return
    
    if len(password) < 6:
        ui.notify("Password must be at least 6 characters long", color="red")
        return
    
    try:
        response = requests.post(
            "http://localhost:8000/signup", 
            data={"username": username.strip(), "password": password}
        )
        
        if response.status_code in (200, 201):
            ui.notify("✅ Account created successfully!", color="green")
            ui.navigate.to("/login")
        else:
            data = handle_api_response(response)
            
    except requests.RequestException as e:
        ui.notify(f"❌ Connection error: {str(e)}", color="red")
        print(f"Signup error: {e}")

def delete_task(task_id: int, task_area):
    global token
    
    if not token:
        ui.notify("❌ You must log in first!", color="red")
        return
    
    def confirm_delete():
        try:
            response = requests.delete(
                f"http://localhost:8000/tasks?id={task_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                ui.notify("✅ Task deleted successfully", color="green")
                list_tasks(task_area)
            else:
                handle_api_response(response)
                
        except requests.RequestException as e:
            ui.notify(f"❌ Connection error: {str(e)}", color="red")
            print(f"Delete error: {e}")
    
    with ui.dialog() as dialog, ui.card().classes("p-6 w-[380px] rounded-2xl shadow-lg"):
        ui.label("🗑️ Confirm Deletion").classes("text-lg font-semibold mb-4 text-center text-gray-700")
        ui.label("Are you sure you want to delete this task? This action cannot be undone.").classes("text-sm text-gray-600 mb-4 text-center")
        
        with ui.row().classes("justify-center gap-3"):
            ui.button("Cancel", on_click=dialog.close).classes(
                "bg-gray-200 text-gray-700 hover:bg-gray-300 px-4 py-2 rounded-lg transition-colors"
            )
            ui.button(
                "Delete",
                on_click=lambda: [confirm_delete(), dialog.close()]
            ).classes("bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors")
    
    dialog.open()

def update_task(task_area, task_id: int, title_input, description_input, due_date_input, priority_input=None):
    global token
    
    if not title_input.value.strip():
        ui.notify("❌ Task title cannot be empty", color="red")
        return
    
    try:
        due_date_value = None
        if due_date_input.value:
            if isinstance(due_date_input.value, str):
                due_date_value = due_date_input.value
            else:
                due_date_value = due_date_input.value.isoformat()
        
        data = {
            "title": title_input.value.strip(),
            "description": description_input.value.strip(),
            "due_date": due_date_value
        }
        
        if priority_input:
            data["priority"] = priority_input.value
        
        response = requests.put(
            f"http://localhost:8000/tasks?id={task_id}",
            headers={"Authorization": f"Bearer {token}"},
            json=data
        )
        
        if response.status_code == 200:
            ui.notify("✅ Task updated successfully", color="green")
            title_input.value = ""
            description_input.value = ""
            due_date_input.value = None
            if priority_input:
                priority_input.value = priorityEnum.Low.value
            list_tasks(task_area)
        else:
            handle_api_response(response)
            
    except requests.RequestException as e:
        ui.notify(f"❌ Connection error: {str(e)}", color="red")
        print(f"Update error: {e}")

def update_task_ui(task_area, task_id: int, current_title: str, current_desc: str, current_due: str, current_priority: str = "Low"):
    with ui.dialog() as dialog, ui.card().classes("p-6 w-[480px] rounded-2xl shadow-lg"):
        ui.label("✏️ Edit Task").classes("text-lg font-semibold mb-4 text-center text-gray-700")

        title_input = ui.input("Title", value=current_title).props("outlined dense").classes("w-full mb-3")
        description_input = ui.textarea("Description", value=current_desc).props("outlined autogrow").classes("w-full mb-3")
        
        date_value = None
        if current_due:
            try:
                if isinstance(current_due, str) and current_due != "None":
                    date_value = current_due.split('T')[0] if 'T' in current_due else current_due
            except:
                pass
        
        due_date_input = ui.date(value=date_value).props("outlined dense clearable").classes("w-full mb-4")
        
        priority_input = ui.select(
            label="Priority",
            options=[p.value for p in priorityEnum],
            value=current_priority
        ).props("outlined dense").classes("w-full mb-4")

        with ui.row().classes("justify-end gap-3"):
            ui.button("Cancel", on_click=dialog.close).classes(
                "bg-gray-200 text-gray-700 hover:bg-gray-300 px-4 py-2 rounded-lg transition-colors"
            )
            ui.button(
                "Save Changes",
                on_click=lambda: [
                    update_task(task_area, task_id, title_input, description_input, due_date_input, priority_input),
                    dialog.close()
                ]
            ).classes("bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors")

    dialog.open()

def update_task_status(status: str, task_area, task_id: int):
    global token
    
    try:
        response = requests.put(
            f"http://localhost:8000/tasks?id={task_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"statue": status}
        )
        
        if response.status_code == 200:
            ui.notify(f"✅ Task marked as {status.lower()}", color="green")
            list_tasks(task_area)
        else:
            handle_api_response(response)
            
    except requests.RequestException as e:
        ui.notify(f"❌ Connection error: {str(e)}", color="red")
        print(f"Status update error: {e}")

def format_date(date_string: str) -> str:
    if not date_string or date_string == "None":
        return ""
    
    try:
        if 'T' in date_string:
            date_obj = datetime.datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        else:
            date_obj = datetime.datetime.strptime(date_string, "%Y-%m-%d")
        
        return date_obj.strftime("%B %d, %Y")
    except:
        return date_string

def sort_tasks_by_priority(tasks: list) -> list:
    priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
    return sorted(tasks, key=lambda t: priority_order.get(t.get('priority', 'Low'), 2))

def list_tasks(task_area):
    global token, current_user
    
    if not token:
        ui.notify("❌ You must log in first!", color="red")
        return    

    try:
        response = requests.get("http://localhost:8000/tasks", headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            tasks = response.json()
            task_area.clear()

            with task_area:
                with ui.row().classes("justify-between items-center w-full mb-6"):
                    with ui.column():
                        ui.label("📋 Your Tasks").classes("text-3xl font-bold text-gray-800")
                        if current_user:
                            ui.label(f"Welcome back, {current_user}! 👋").classes("text-sm text-gray-600")
                    
                    ui.button("🚪 Logout", on_click=logout).classes(
                        "bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
                    )
                
                with ui.row().classes("justify-center mb-6"):
                    with ui.dialog() as add_dialog, ui.card().classes("p-8 w-[500px] rounded-2xl shadow-xl"):
                        ui.label("➕ Create New Task").classes("text-2xl font-bold mb-6 text-center text-gray-800")

                        title_input = ui.input("Task Title", placeholder="task title").props("outlined").classes("w-full mb-4")
                        description_input = ui.textarea("Description", placeholder="Add more details (optional)...").props("outlined autogrow").classes("w-full mb-4")
                        
                        with ui.row().classes("gap-4 mb-4"):
                            due_date_input = ui.date("Due Date").props("outlined clearable").classes("flex-1")
                            priority_input = ui.select(
                                label="Priority",
                                options=[p.value for p in priorityEnum],
                                value=priorityEnum.Low.value
                            ).props("outlined").classes("flex-1")

                        with ui.row().classes("justify-end gap-3 mt-6"):
                            ui.button("Cancel", on_click=add_dialog.close).classes(
                                "bg-gray-200 text-gray-700 hover:bg-gray-300 px-6 py-3 rounded-lg transition-colors"
                            )
                            ui.button(
                                "Create Task",
                                on_click=lambda: add_task(
                                    title_input=title_input,
                                    description_input=description_input,
                                    priority_input=priority_input,
                                    due_date_input=due_date_input,
                                    task_area=task_area,
                                    dialog=add_dialog
                                )
                            ).classes("bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg transition-colors font-semibold")
                    with ui.dialog() as ai_dialog, ui.card().classes("p-8 w-[500px] rounded-2xl shadow-xl"):
                        ui.label("➕ Create New Task with IA").classes("text-2xl font-bold mb-6 text-center text-gray-800")
                        user_input =ui.input("AI Task Description", placeholder="Describe your task in natural language...")
                        ui.button("creat task",on_click=lambda e:ai_creat_task(dialog=ai_dialog,task_area=task_area,user_input=user_input,button=e.sender))
                ui.button("➕ Create New Task", on_click=add_dialog.open).classes(
                    "bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white px-8 py-4 rounded-xl shadow-lg w-full text-lg font-semibold transition-all transform hover:scale-105"
                )
                ui.button("🧠 Create Task with AI",on_click=ai_dialog.open).classes(
                    "bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white px-8 py-4 rounded-xl shadow-lg w-full text-lg font-semibold transition-all transform hover:scale-105"
                )

                if not tasks:
                    with ui.column().classes("items-center mt-16"):
                        ui.icon("assignment", size="5rem").classes("text-gray-300 mb-6")
                        ui.label("No tasks yet").classes("text-2xl text-gray-500 mb-2 font-semibold")
                        ui.label("Create your first task to get started! 🚀").classes("text-gray-400")
                    return

                total_tasks = len(tasks)
                completed_tasks = len([t for t in tasks if t.get('status', t.get('statue', '')).lower() == 'completed'])
                pending_tasks = total_tasks - completed_tasks
                
                with ui.row().classes("w-full max-w-5xl mx-auto gap-8 mt-8").style("display:flex;"):
                    with ui.card().classes("p-4 bg-blue-50 border border-blue-200 rounded-xl").style("min-width: 120px;"):
                        ui.label(f"📊 Total: {total_tasks}").classes("text-blue-700 font-semibold")
                    with ui.card().classes("p-4 bg-orange-50 border border-orange-200 rounded-xl").style("min-width: 120px;"):
                        ui.label(f"⏳ Pending: {pending_tasks}").classes("text-orange-700 font-semibold")
                    with ui.card().classes("p-4 bg-green-50 border border-green-200 rounded-xl").style("min-width: 120px;"):
                        ui.label(f"✅ Completed: {completed_tasks}").classes("text-green-700 font-semibold")

                with ui.row().classes("w-full max-w-5xl mx-auto gap-8 mt-8").style("display:flex;"):
                    pending_tasks_list = [t for t in tasks if t.get('status', t.get('statue', '')).lower() != 'completed']
                    completed_tasks_list = [t for t in tasks if t.get('status', t.get('statue', '')).lower() == 'completed']
                    pending_tasks_list = sort_tasks_by_priority(pending_tasks_list)
                    completed_tasks_list = sort_tasks_by_priority(completed_tasks_list)
                    
                    with ui.column().classes("flex-1 space-y-4"):
                        if pending_tasks_list:
                            ui.label("🔄 Active Tasks").classes("text-2xl font-bold text-gray-700 mb-4")
                            for task in pending_tasks_list:
                                create_task_card(task, task_area, False)
                        else:
                            ui.label("No active tasks").classes("text-gray-500 italic")
                    
                    with ui.column().classes("flex-1 space-y-4"):
                        if completed_tasks_list:
                            ui.label("✅ Completed Tasks").classes("text-2xl font-bold text-green-600 mb-4")
                            for task in completed_tasks_list:
                                create_task_card(task, task_area, True)
                        else:
                            ui.label("No completed tasks").classes("text-gray-500 italic")

        else:
            handle_api_response(response)
            
    except requests.RequestException as e:
        ui.notify(f"❌ Connection error: {str(e)}", color="red")
        print(f"List tasks error: {e}")

def create_task_card(task: Dict, task_area, is_completed: bool):
    due_date_display = format_date(task.get('due_date', ''))
    priority = task.get('priority', 'Low')
    priority_config = get_priority_display(priority)
    
    if is_completed:
        card_classes = "w-full rounded-2xl shadow-md bg-gray-50 border border-gray-200 opacity-75"
    else:
        card_classes = f"w-full rounded-2xl shadow-md hover:shadow-lg transition-all bg-white border-2 {priority_config['border_color']}"
    
    with ui.card().classes(card_classes):
        with ui.column().classes("p-6"):
            with ui.row().classes("justify-between items-start mb-4"):
                with ui.column().classes("flex-1"):
                    with ui.row().classes("items-center gap-3 mb-2"):
                        ui.html(f"""
                            <span class="px-3 py-1 rounded-full text-xs font-bold {priority_config['badge_class']}">
                                {priority_config['icon']} {priority}
                            </span>
                        """)
                        
                        if is_completed:
                            ui.label("✅ Completed").classes("px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full font-semibold")
                    
                    title_class = "text-xl font-bold text-gray-800" if not is_completed else "text-xl font-bold text-gray-500 line-through"
                    ui.label(task['title']).classes(title_class)
                
                with ui.row().classes("gap-2"):
                    ui.button(
                        '✏️ Edit',
                        on_click=lambda taskid=task['id']: update_task_ui(
                            task_area,
                            taskid,
                            task['title'],
                            task.get('description', task.get('descreption', '')),
                            task.get('due_date', ''),
                            task.get('priority', 'Low')
                        ),
                    ).classes("bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-lg text-sm transition-colors").props("size=sm")
                    
                    ui.button(
                        '🗑️ Delete',
                        on_click=lambda taskid=task['id']: delete_task(taskid, task_area),
                    ).classes("bg-red-500 hover:bg-red-600 text-white p-2 rounded-lg text-sm transition-colors").props("size=sm")
            
            if task.get('description', task.get('descreption', '')):
                description = task.get('description', task.get('descreption', ''))
                desc_class = "text-gray-700 mb-4 bg-gray-50 p-3 rounded-lg" if not is_completed else "text-gray-500 mb-4 bg-gray-50 p-3 rounded-lg"
                ui.label(description).classes(desc_class)
            
            with ui.row().classes("justify-between items-center"):
                with ui.column():
                    if due_date_display:
                        due_class = "text-gray-600 text-sm font-medium" if not is_completed else "text-gray-400 text-sm"
                        ui.label(f"📅 Due: {due_date_display}").classes(due_class)
                
                current_status = task.get('status', task.get('statue', 'Pending'))
                ui.checkbox(
                    'Mark as completed',
                    value=(current_status.lower() == 'completed'),
                    on_change=lambda e, taskid=task['id']: update_task_status(
                        'Completed' if e.value else 'Pending',
                        task_area,
                        taskid
                    ),
                ).classes("text-sm font-medium")

def add_task(title_input, description_input, due_date_input, priority_input, task_area, dialog):
    global token
    
    if not title_input.value.strip():
        ui.notify("❌ Task title cannot be empty", color="red")
        return
    
    try:
        due_date_value = None
        if due_date_input.value:
            if isinstance(due_date_input.value, str):
                due_date_value = due_date_input.value
            else:
                due_date_value = due_date_input.value.isoformat()
        
        data = {
            "title": title_input.value.strip(),
            "description": description_input.value.strip(),
            "due_date": due_date_value,
            "priority": priority_input.value
        }
        
        response = requests.post("http://localhost:8000/tasks", json=data, headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            ui.notify("✅ Task created successfully!", color="green")
            dialog.close()
            title_input.value = ""
            description_input.value = ""
            due_date_input.value = None
            priority_input.value = priorityEnum.Low.value
            list_tasks(task_area)
        else:
            handle_api_response(response)
            
    except requests.RequestException as e:
        ui.notify(f"❌ Connection error: {str(e)}", color="red")
        print(f"Add task error: {e}")
        
def ai_creat_task(dialog,task_area,user_input,button):
    if not user_input.value.strip():
        ui.notify("❌ Task title cannot be empty", color="red")
        return
    button.props("loading")  
    
    
    
    response = requests.post("http://localhost:8000/ai_creat", params={"user_input": user_input.value}, headers={"Authorization": f"Bearer {token}"})
    if response.status_code == 200:
        
        ui.notify("✅ Task created successfully!", color="green")
        
        dialog.close()
        user_input.value = ""
        list_tasks(task_area)
    else:
        handle_api_response(response)
    
    button.props(remove="loading")
        

def logout():
    global token, current_user
    token = None
    current_user = None
    ui.notify("👋 Logged out successfully!", color="green")
    ui.navigate.to("/login")
