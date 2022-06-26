from django.contrib import admin

from .models import User, InstructorProfile, StudentProfile, Course

# class ModuleInline(admin.StackedInline):
#     model = Module


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor']
    list_filter = ['created']
    search_fields = ['title', 'overview']
    prepopulated_fields = {'slug': ('title',)}
    # inlines = [ModuleInline]


admin.site.register(User)
admin.site.register(InstructorProfile)
admin.site.register(StudentProfile)
