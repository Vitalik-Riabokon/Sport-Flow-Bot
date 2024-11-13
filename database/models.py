from sqlalchemy import (DECIMAL, BigInteger, CheckConstraint, Date, ForeignKey, Integer, String)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        String,
        CheckConstraint("status IN ('client', 'admin', 'creator')"),
        nullable=False,
    )
    registration_date: Mapped[Date] = mapped_column(Date, nullable=False)


class Shift(Base):
    __tablename__ = "shifts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"))
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    start_time: Mapped[Date] = mapped_column(Date)
    end_time: Mapped[Date | None] = mapped_column(Date)

    shift_users: Mapped["Users"] = relationship(backref="shifts")


class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    product_name: Mapped[str] = mapped_column(String, nullable=False)
    photo: Mapped[str | None]
    description: Mapped[str | None]
    price: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    status_product: Mapped[str | None]


class Payment(Base):
    __tablename__ = "payments"

    payment_id: Mapped[int] = mapped_column(
        Integer, primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.product_id"))
    price: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(
        String, CheckConstraint("payment_method IN ('card', 'cash')"), nullable=False
    )
    payment_date: Mapped[Date] = mapped_column(Date, nullable=False)
    expiration_date: Mapped[Date] = mapped_column(Date, nullable=False)

    payments_users: Mapped["Users"] = relationship(backref="payments")
    payments_product: Mapped["Product"] = relationship(backref="payments")


class Trainer(Base):
    __tablename__ = "trainers"

    trainer_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), unique=True
    )

    trainers_users: Mapped["Users"] = relationship(backref="trainers")


class TrainerClient(Base):
    __tablename__ = "trainer_clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trainer_id: Mapped[int] = mapped_column(Integer, ForeignKey("trainers.trainer_id"))
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), unique=True)
    price_per_session: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    start_date: Mapped[Date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Date | None] = mapped_column(Date)

    trainer_clients_trainer: Mapped["Trainer"] = relationship(backref="trainer_clients")
    trainer_clients_users: Mapped["Users"] = relationship(backref="trainer_clients")


class TrainingSession(Base):
    __tablename__ = "training_sessions"

    session_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    client_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("trainer_clients.client_id")
    )
    trainer_id: Mapped[int] = mapped_column(Integer, ForeignKey("trainers.trainer_id"))
    price_session: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(
        String, CheckConstraint("payment_method IN ('card', 'cash')"), nullable=False
    )
    session_date: Mapped[Date] = mapped_column(Date, nullable=False)

    training_sessions_trainer_client: Mapped["TrainerClient"] = relationship(
        backref="training_sessions"
    )
    training_sessions_trainer: Mapped["Trainer"] = relationship(
        backref="training_sessions"
    )


class Program(Base):
    __tablename__ = "programs"

    program_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    trainer_id: Mapped[int] = mapped_column(Integer, ForeignKey("trainers.trainer_id"))
    client_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("trainer_clients.client_id")
    )
    program_file: Mapped[str] = mapped_column(String, nullable=False)
    program_date: Mapped[Date] = mapped_column(Date, nullable=False)

    programs_trainer: Mapped["Trainer"] = relationship(backref="programs")
    programs_trainer_client: Mapped["TrainerClient"] = relationship(backref="programs")


class ProgramDetail(Base):
    __tablename__ = "program_details"

    program_details_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    program_id: Mapped[int] = mapped_column(Integer, ForeignKey("programs.program_id"))
    training_number: Mapped[int]
    approaches_number: Mapped[str]
    repetitions_number: Mapped[str]
    weight: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2), nullable=False)
    program_status: Mapped[str | None]

    program_details_trainer_client: Mapped["Program"] = relationship(
        backref="program_details")
