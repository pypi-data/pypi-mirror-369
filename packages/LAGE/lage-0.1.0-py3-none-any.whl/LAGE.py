import math
import os, shutil
from datetime import date, datetime
import pytz

class Math:
    @staticmethod
    def sqrt(num):
        return math.sqrt(num)

    @staticmethod
    def pow(base, exponent):
        return math.pow(base, exponent)
    
    @staticmethod
    def exp(num):
        return math.exp(num)
    
    @staticmethod
    def sin(num):
        return math.sin(num)

    @staticmethod
    def cos(num):
        return math.cos(num)

    @staticmethod
    def PI(num):
        return math.pi * (num ** 2)
    
    @staticmethod
    def MCM(num, num2):
        return math.gcd(num, num2)
    
class System():
    @staticmethod
    def current_directory():
        return os.getcwd()
    
    @staticmethod
    def change_directory(path):
        return os.chdir(path)
    
    @staticmethod
    def make_directory(path):
        return os.makedirs(path, exist_ok=True)
    
    @staticmethod
    def rename_directory(path, path2):
        return os.rename(path, path2)
    
    @staticmethod
    def move_directory(path, path2):
        return shutil.move(path, path2)
    
    @staticmethod
    def delete_directory(path):
        return shutil.rmtree(path)
    
    @staticmethod
    def copy_directory(path, path2):
        return shutil.copytree(path, path2)
    
    @staticmethod
    def make_file(filename, mode = "w", content=0):
        with open(filename, mode) as file:
            file.write(str(content))
            file.close()
    
    @staticmethod
    def file_readline(filename, mode='r'):
        lines = []
        with open(filename, mode) as f:
            for line in f:
                lines.append(line.strip())
        return lines
    
    @staticmethod
    def copy_file(path, path2):
        return shutil.copy(path, path2)

    @staticmethod
    def move_file(path, path2):
        return shutil.move(path, path2)

    @staticmethod
    def rename_file(path, name):
        return os.rename(path, name)
    
    @staticmethod
    def delete_file(path):
        return os.unlink(path)
    
    def get_environ_path(value):
        return os.getenv(value)
    
    @staticmethod
    def create_environ_path(name, value):
        os.environ[name] = value
        return name, value
    
    @staticmethod
    def delete_environ_path(name):
        os.environ.pop(name, None)

    @staticmethod
    def get_file_permission(file, type=0o6464):
        os.chmod(file, type)

    @staticmethod
    def get_file_attribute(file):
        stat = os.stat(file)
        return stat.st_size, stat.st_mtime

class Time:
    @staticmethod
    def jet_lag(position):
        return pytz.timezone(position)
    
    @staticmethod
    def jet_lag_time(position):
        return datetime.datetime.now(pytz.timezone(position))

    @staticmethod
    def current_datetime():
        return datetime.now()
    
    @staticmethod
    def current_data():
        return datetime.now().date()
    
    @staticmethod
    def format_time_data(data, format_input, format_output):
        date_obj = datetime.strptime(data, format_input)
        return date_obj.strftime(format_output)
    
    @staticmethod
    def calculate_age(current_year, year):
        age = current_year - year
        return age
