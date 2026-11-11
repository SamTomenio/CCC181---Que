from datetime import datetime, time

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (CheckConstraint, DateTime, ForeignKey, Index,
                        String, Time, func, text)
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class Company(db.Model):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    trucks: Mapped[list["Truck"]] = relationship(back_populates="company")


class Truck(db.Model):
    __tablename__ = "trucks"
    __table_args__ = (
        CheckConstraint("plate ~ '^[A-Z0-9 -]{4,12}$'", name="ck_trucks_plate"),
        CheckConstraint(
            "vehicle_type IN ('4-wheeler','6-wheeler','8-wheeler','10-wheeler','trailer','other')",
            name="ck_trucks_vehicle_type"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    plate: Mapped[str] = mapped_column(String(12), unique=True)
    vehicle_type: Mapped[str] = mapped_column(String(20), default="other")
    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"))
    company: Mapped["Company | None"] = relationship(back_populates="trucks")
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="truck")


class Service(db.Model):
    __tablename__ = "services"
    __table_args__ = (
        CheckConstraint("avg_minutes > 0", name="ck_services_avg_minutes"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)
    avg_minutes: Mapped[int]
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="service")


class Ticket(db.Model):
    __tablename__ = "tickets"
    __table_args__ = (
        CheckConstraint(
            "status IN ('waiting','called','served','left')",
            name="ck_tickets_status"),
        Index("uq_one_open_ticket_per_truck", "truck_id", unique=True,
              postgresql_where=text("status IN ('waiting','called')")),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    driver_name: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(10), default="waiting")
    bay: Mapped[str | None] = mapped_column(String(20))
    arrive_by: Mapped[time | None] = mapped_column(Time)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    called_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    driver_ok_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    driver_deleted: Mapped[bool] = mapped_column(default=False)
    truck_id: Mapped[int] = mapped_column(
        ForeignKey("trucks.id", ondelete="RESTRICT"))
    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id", ondelete="RESTRICT"))
    truck: Mapped["Truck"] = relationship(back_populates="tickets")
    service: Mapped["Service"] = relationship(back_populates="tickets")