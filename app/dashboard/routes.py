from flask import Blueprint, render_template_string, session, flash, redirect, url_for
from app.dashboard.auth import login_required
from app.db.queries import (
    get_dashboard_stats, get_recent_appointments, get_urgent_messages, 
    get_recent_images, get_all_feedback
)
import logging

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Dashboard principal con estadísticas y resumen."""
    try:
        stats = get_dashboard_stats()
        recent_appointments = get_recent_appointments(5)
        urgent_messages = get_urgent_messages(5)
        recent_images = get_recent_images(5)
        
        return render_template_string(DASHBOARD_TEMPLATE, 
                                    stats=stats,
                                    recent_appointments=recent_appointments,
                                    urgent_messages=urgent_messages,
                                    recent_images=recent_images,
                                    user=session)
    except Exception as e:
        logging.error(f"Error loading dashboard: {e}")
        flash('Error al cargar el dashboard.', 'error')
        return redirect(url_for('auth.login'))

@dashboard_bp.route('/dashboard/appointments')
@login_required
def appointments():
    """Página de turnos con lista completa."""
    try:
        appointments = get_recent_appointments(50)
        return render_template_string(APPOINTMENTS_TEMPLATE, 
                                    appointments=appointments,
                                    user=session)
    except Exception as e:
        logging.error(f"Error loading appointments: {e}")
        flash('Error al cargar los turnos.', 'error')
        return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/dashboard/urgent')
@login_required
def urgent():
    """Página de mensajes urgentes."""
    try:
        urgent_messages = get_urgent_messages(50)
        return render_template_string(URGENT_TEMPLATE, 
                                    urgent_messages=urgent_messages,
                                    user=session)
    except Exception as e:
        logging.error(f"Error loading urgent messages: {e}")
        flash('Error al cargar los mensajes urgentes.', 'error')
        return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/dashboard/images')
@login_required
def images():
    """Página de imágenes subidas por pacientes."""
    try:
        images = get_recent_images(50)
        return render_template_string(IMAGES_TEMPLATE, 
                                    images=images,
                                    user=session)
    except Exception as e:
        logging.error(f"Error loading images: {e}")
        flash('Error al cargar las imágenes.', 'error')
        return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/dashboard/feedback')
@login_required
def feedback():
    """Página de feedback de pacientes."""
    try:
        feedbacks = get_all_feedback()
        return render_template_string(FEEDBACK_TEMPLATE, 
                                    feedbacks=feedbacks,
                                    user=session)
    except Exception as e:
        logging.error(f"Error loading feedback: {e}")
        flash('Error al cargar el feedback.', 'error')
        return redirect(url_for('dashboard.index'))

# Templates HTML
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard Médico</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        .sidebar { min-height: 100vh; background-color: #343a40; }
        .sidebar .nav-link { color: #adb5bd; }
        .sidebar .nav-link:hover { color: #fff; }
        .sidebar .nav-link.active { color: #fff; background-color: #495057; }
        .main-content { padding: 20px; }
        .stat-card { border-left: 4px solid #007bff; }
        .stat-card.warning { border-left-color: #ffc107; }
        .stat-card.danger { border-left-color: #dc3545; }
        .stat-card.success { border-left-color: #28a745; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-3 col-lg-2 d-md-block sidebar collapse">
                <div class="position-sticky pt-3">
                    <div class="text-center mb-4">
                        <h5 class="text-white">Dashboard Médico</h5>
                        <small class="text-muted">Bienvenido, {{ user.full_name }}</small>
                    </div>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link active" href="{{ url_for('dashboard.index') }}">
                                <i class="bi bi-house"></i> Inicio
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard.appointments') }}">
                                <i class="bi bi-calendar"></i> Turnos
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard.urgent') }}">
                                <i class="bi bi-exclamation-triangle"></i> Urgencias
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard.images') }}">
                                <i class="bi bi-image"></i> Imágenes
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard.feedback') }}">
                                <i class="bi bi-chat"></i> Feedback
                            </a>
                        </li>
                        <li class="nav-item mt-3">
                            <a class="nav-link" href="{{ url_for('auth.logout') }}">
                                <i class="bi bi-box-arrow-right"></i> Cerrar Sesión
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>

            <!-- Main content -->
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 main-content">
                <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                    <h1 class="h2">Dashboard</h1>
                </div>

                <!-- Stats Cards -->
                <div class="row mb-4">
                    <div class="col-xl-3 col-md-6 mb-4">
                        <div class="card stat-card border-0 shadow h-100 py-2">
                            <div class="card-body">
                                <div class="row no-gutters align-items-center">
                                    <div class="col mr-2">
                                        <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                                            Turnos Hoy</div>
                                        <div class="h5 mb-0 font-weight-bold text-gray-800">{{ stats.appointments_today or 0 }}</div>
                                    </div>
                                    <div class="col-auto">
                                        <i class="bi bi-calendar-check fa-2x text-gray-300"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-xl-3 col-md-6 mb-4">
                        <div class="card stat-card warning border-0 shadow h-100 py-2">
                            <div class="card-body">
                                <div class="row no-gutters align-items-center">
                                    <div class="col mr-2">
                                        <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">
                                            Pendientes</div>
                                        <div class="h5 mb-0 font-weight-bold text-gray-800">{{ stats.pending_appointments or 0 }}</div>
                                    </div>
                                    <div class="col-auto">
                                        <i class="bi bi-clock fa-2x text-gray-300"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-xl-3 col-md-6 mb-4">
                        <div class="card stat-card danger border-0 shadow h-100 py-2">
                            <div class="card-body">
                                <div class="row no-gutters align-items-center">
                                    <div class="col mr-2">
                                        <div class="text-xs font-weight-bold text-danger text-uppercase mb-1">
                                            Ausencias</div>
                                        <div class="h5 mb-0 font-weight-bold text-gray-800">{{ stats.recent_absences or 0 }}</div>
                                    </div>
                                    <div class="col-auto">
                                        <i class="bi bi-x-circle fa-2x text-gray-300"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-xl-3 col-md-6 mb-4">
                        <div class="card stat-card success border-0 shadow h-100 py-2">
                            <div class="card-body">
                                <div class="row no-gutters align-items-center">
                                    <div class="col mr-2">
                                        <div class="text-xs font-weight-bold text-success text-uppercase mb-1">
                                            Feedback</div>
                                        <div class="h5 mb-0 font-weight-bold text-gray-800">{{ stats.recent_feedback or 0 }}</div>
                                    </div>
                                    <div class="col-auto">
                                        <i class="bi bi-chat-dots fa-2x text-gray-300"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Recent Data -->
                <div class="row">
                    <div class="col-lg-6">
                        <div class="card shadow mb-4">
                            <div class="card-header py-3">
                                <h6 class="m-0 font-weight-bold text-primary">Turnos Recientes</h6>
                            </div>
                            <div class="card-body">
                                {% if recent_appointments %}
                                    <div class="table-responsive">
                                        <table class="table table-sm">
                                            <thead>
                                                <tr>
                                                    <th>Paciente</th>
                                                    <th>Fecha</th>
                                                    <th>Estado</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {% for app in recent_appointments %}
                                                <tr>
                                                    <td>{{ app[0] }}</td>
                                                    <td>{{ app[2].strftime('%d/%m/%Y %H:%M') }}</td>
                                                    <td><span class="badge bg-{{ 'success' if app[3] == 'confirmado' else 'warning' }}">{{ app[3] }}</span></td>
                                                </tr>
                                                {% endfor %}
                                            </tbody>
                                        </table>
                                    </div>
                                {% else %}
                                    <p class="text-muted">No hay turnos recientes.</p>
                                {% endif %}
                            </div>
                        </div>
                    </div>

                    <div class="col-lg-6">
                        <div class="card shadow mb-4">
                            <div class="card-header py-3">
                                <h6 class="m-0 font-weight-bold text-danger">Mensajes Urgentes</h6>
                            </div>
                            <div class="card-body">
                                {% if urgent_messages %}
                                    <div class="table-responsive">
                                        <table class="table table-sm">
                                            <thead>
                                                <tr>
                                                    <th>Paciente</th>
                                                    <th>Teléfono</th>
                                                    <th>Fecha</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {% for msg in urgent_messages %}
                                                <tr>
                                                    <td>{{ msg[0] }}</td>
                                                    <td>{{ msg[1] }}</td>
                                                    <td>{{ msg[2].strftime('%d/%m/%Y') }}</td>
                                                </tr>
                                                {% endfor %}
                                            </tbody>
                                        </table>
                                    </div>
                                {% else %}
                                    <p class="text-muted">No hay mensajes urgentes.</p>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

APPOINTMENTS_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Turnos - Dashboard Médico</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        .sidebar { min-height: 100vh; background-color: #343a40; }
        .sidebar .nav-link { color: #adb5bd; }
        .sidebar .nav-link:hover { color: #fff; }
        .sidebar .nav-link.active { color: #fff; background-color: #495057; }
        .main-content { padding: 20px; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-3 col-lg-2 d-md-block sidebar collapse">
                <div class="position-sticky pt-3">
                    <div class="text-center mb-4">
                        <h5 class="text-white">Dashboard Médico</h5>
                        <small class="text-muted">Bienvenido, {{ user.full_name }}</small>
                    </div>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard.index') }}">
                                <i class="bi bi-house"></i> Inicio
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link active" href="{{ url_for('dashboard.appointments') }}">
                                <i class="bi bi-calendar"></i> Turnos
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard.urgent') }}">
                                <i class="bi bi-exclamation-triangle"></i> Urgencias
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard.images') }}">
                                <i class="bi bi-image"></i> Imágenes
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard.feedback') }}">
                                <i class="bi bi-chat"></i> Feedback
                            </a>
                        </li>
                        <li class="nav-item mt-3">
                            <a class="nav-link" href="{{ url_for('auth.logout') }}">
                                <i class="bi bi-box-arrow-right"></i> Cerrar Sesión
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>

            <!-- Main content -->
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 main-content">
                <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                    <h1 class="h2">Turnos</h1>
                </div>

                <div class="card shadow">
                    <div class="card-body">
                        {% if appointments %}
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Paciente</th>
                                            <th>Teléfono</th>
                                            <th>Fecha y Hora</th>
                                            <th>Estado</th>
                                            <th>Especialidad</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for app in appointments %}
                                        <tr>
                                            <td>{{ app[0] }}</td>
                                            <td>{{ app[1] }}</td>
                                            <td>{{ app[2].strftime('%d/%m/%Y %H:%M') }}</td>
                                            <td><span class="badge bg-{{ 'success' if app[3] == 'confirmado' else 'warning' if app[3] == 'pendiente' else 'secondary' }}">{{ app[3] }}</span></td>
                                            <td>{{ app[4] or 'No especificada' }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        {% else %}
                            <p class="text-muted text-center">No hay turnos registrados.</p>
                        {% endif %}
                    </div>
                </div>
            </main>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

URGENT_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Urgencias - Dashboard Médico</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        .sidebar { min-height: 100vh; background-color: #343a40; }
        .sidebar .nav-link { color: #adb5bd; }
        .sidebar .nav-link:hover { color: #fff; }
        .sidebar .nav-link.active { color: #fff; background-color: #495057; }
        .main-content { padding: 20px; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-3 col-lg-2 d-md-block sidebar collapse">
                <div class="position-sticky pt-3">
                    <div class="text-center mb-4">
                        <h5 class="text-white">Dashboard Médico</h5>
                        <small class="text-muted">Bienvenido, {{ user.full_name }}</small>
                    </div>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard.index') }}">
                                <i class="bi bi-house"></i> Inicio
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard.appointments') }}">
                                <i class="bi bi-calendar"></i> Turnos
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link active" href="{{ url_for('dashboard.urgent') }}">
                                <i class="bi bi-exclamation-triangle"></i> Urgencias
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard.images') }}">
                                <i class="bi bi-image"></i> Imágenes
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard.feedback') }}">
                                <i class="bi bi-chat"></i> Feedback
                            </a>
                        </li>
                        <li class="nav-item mt-3">
                            <a class="nav-link" href="{{ url_for('auth.logout') }}">
                                <i class="bi bi-box-arrow-right"></i> Cerrar Sesión
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>

            <!-- Main content -->
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 main-content">
                <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                    <h1 class="h2">Mensajes Urgentes</h1>
                </div>

                <div class="card shadow">
                    <div class="card-body">
                        {% if urgent_messages %}
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Paciente</th>
                                            <th>Teléfono</th>
                                            <th>Fecha</th>
                                            <th>Estado</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for msg in urgent_messages %}
                                        <tr>
                                            <td>{{ msg[0] }}</td>
                                            <td>{{ msg[1] }}</td>
                                            <td>{{ msg[2].strftime('%d/%m/%Y %H:%M') }}</td>
                                            <td><span class="badge bg-danger">Urgente</span></td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        {% else %}
                            <p class="text-muted text-center">No hay mensajes urgentes.</p>
                        {% endif %}
                    </div>
                </div>
            </main>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

IMAGES_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Imágenes - Dashboard Médico</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        .sidebar { min-height: 100vh; background-color: #343a40; }
        .sidebar .nav-link { color: #adb5bd; }
        .sidebar .nav-link:hover { color: #fff; }
        .sidebar .nav-link.active { color: #fff; background-color: #495057; }
        .main-content { padding: 20px; }
        .image-thumbnail { max-width: 100px; max-height: 100px; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-3 col-lg-2 d-md-block sidebar collapse">
                <div class="position-sticky pt-3">
                    <div class="text-center mb-4">
                        <h5 class="text-white">Dashboard Médico</h5>
                        <small class="text-muted">Bienvenido, {{ user.full_name }}</small>
                    </div>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard.index') }}">
                                <i class="bi bi-house"></i> Inicio
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard.appointments') }}">
                                <i class="bi bi-calendar"></i> Turnos
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard.urgent') }}">
                                <i class="bi bi-exclamation-triangle"></i> Urgencias
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link active" href="{{ url_for('dashboard.images') }}">
                                <i class="bi bi-image"></i> Imágenes
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard.feedback') }}">
                                <i class="bi bi-chat"></i> Feedback
                            </a>
                        </li>
                        <li class="nav-item mt-3">
                            <a class="nav-link" href="{{ url_for('auth.logout') }}">
                                <i class="bi bi-box-arrow-right"></i> Cerrar Sesión
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>

            <!-- Main content -->
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 main-content">
                <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                    <h1 class="h2">Imágenes de Pacientes</h1>
                </div>

                <div class="card shadow">
                    <div class="card-body">
                        {% if images %}
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Paciente</th>
                                            <th>Teléfono</th>
                                            <th>Archivo</th>
                                            <th>Fecha</th>
                                            <th>Vista Previa</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for img in images %}
                                        <tr>
                                            <td>{{ img[0] or 'No especificado' }}</td>
                                            <td>{{ img[1] }}</td>
                                            <td>{{ img[2] }}</td>
                                            <td>{{ img[3].strftime('%d/%m/%Y %H:%M') }}</td>
                                            <td>
                                                {% if img[4] %}
                                                    <img src="{{ img[4] }}" class="image-thumbnail" alt="Vista previa">
                                                {% else %}
                                                    <span class="text-muted">No disponible</span>
                                                {% endif %}
                                            </td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        {% else %}
                            <p class="text-muted text-center">No hay imágenes subidas.</p>
                        {% endif %}
                    </div>
                </div>
            </main>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

FEEDBACK_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Feedback - Dashboard Médico</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        .sidebar { min-height: 100vh; background-color: #343a40; }
        .sidebar .nav-link { color: #adb5bd; }
        .sidebar .nav-link:hover { color: #fff; }
        .sidebar .nav-link.active { color: #fff; background-color: #495057; }
        .main-content { padding: 20px; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-3 col-lg-2 d-md-block sidebar collapse">
                <div class="position-sticky pt-3">
                    <div class="text-center mb-4">
                        <h5 class="text-white">Dashboard Médico</h5>
                        <small class="text-muted">Bienvenido, {{ user.full_name }}</small>
                    </div>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard.index') }}">
                                <i class="bi bi-house"></i> Inicio
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard.appointments') }}">
                                <i class="bi bi-calendar"></i> Turnos
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard.urgent') }}">
                                <i class="bi bi-exclamation-triangle"></i> Urgencias
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard.images') }}">
                                <i class="bi bi-image"></i> Imágenes
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link active" href="{{ url_for('dashboard.feedback') }}">
                                <i class="bi bi-chat"></i> Feedback
                            </a>
                        </li>
                        <li class="nav-item mt-3">
                            <a class="nav-link" href="{{ url_for('auth.logout') }}">
                                <i class="bi bi-box-arrow-right"></i> Cerrar Sesión
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>

            <!-- Main content -->
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 main-content">
                <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                    <h1 class="h2">Feedback de Pacientes</h1>
                </div>

                <div class="card shadow">
                    <div class="card-body">
                        {% if feedbacks %}
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Paciente</th>
                                            <th>Teléfono</th>
                                            <th>Fecha</th>
                                            <th>Mensaje</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for feedback in feedbacks %}
                                        <tr>
                                            <td>{{ feedback[0] }}</td>
                                            <td>{{ feedback[1] }}</td>
                                            <td>{{ feedback[2].strftime('%d/%m/%Y %H:%M') }}</td>
                                            <td>{{ feedback[3] }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        {% else %}
                            <p class="text-muted text-center">No hay feedback registrado.</p>
                        {% endif %}
                    </div>
                </div>
            </main>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
''' 