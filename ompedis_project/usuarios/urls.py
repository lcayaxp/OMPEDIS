from django.urls import path
from usuarios.views import login_view, perfil_view, logout_view, dashboard_view, SignUpView
from pacientes.views import lista_pacientes_view  # Importa la vista correspondiente
from reportes.views import menu_reportes_view  # Importa la vista correspondiente
from usuarios.views import UserListView, UserUpdateView, UserDeleteView
from usuarios.views import UserDetailView

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('perfil/', perfil_view, name='perfil'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/edit/<int:pk>/', UserUpdateView.as_view(), name='user_edit'),
    path('users/delete/<int:pk>/', UserDeleteView.as_view(), name='user_delete'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),

    # Ruta para el menú de reportes
    path('menu/', menu_reportes_view, name='menu_reportes'),
    # Si decides incluir las URLs de pacientes aquí, puedes hacerlo así:
    path('pacientes/', lista_pacientes_view, name='lista_pacientes'),
]
