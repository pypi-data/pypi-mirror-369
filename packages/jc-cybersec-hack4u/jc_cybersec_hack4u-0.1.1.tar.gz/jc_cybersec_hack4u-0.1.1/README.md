# Hack4U Acadeny Courses Library

Una biblioteca Python para consultar cursos de la academia Hack4U.

## Cursos disponibles:

- Introcucción al Linux [15 horas]
- Personalización de Linux [15 horas]
- Introducción al Hacking [53 horas]

## Instalación

Instala el paquete usando 'pip3':

```python3
pip3 install hack4u
```

## Uso básico

### Listar todos los cursos

```python
from hack4u import list_courses

for course in list_courses
    print(course)
```

### Obtener un curso por nombre

```python
from hack4u import search_course_by_name

course = search_course_by_name("Introducción al Linux")
print(course)
```

### Calcular duracción total de los cursos

```python3
from hack4u import total_duration

print(f"Duracción total: {total_duration()} horas")
```
