import logging

from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.dispatcher.middlewares.error import ErrorsMiddleware
from aiogram.types import Update


class DataError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"DataError: {self.message}"


class RegistrationError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"RegistrationError: {self.message}"
