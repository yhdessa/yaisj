from fastapi.middleware.cors import CORSMiddleware
import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, Float, String, Date
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, Field
from datetime import date
from typing import List, Dict, Any
import psutil

app = FastAPI(
    title="Expense Tracker + Server Monitor",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "sqlite:///./expenses.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} 
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=date.today, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)


Base.metadata.create_all(bind=engine)

class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Сумма > 0")
    category: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class ExpenseOut(ExpenseCreate):
    id: int
    date: date

    class Config:
        from_attributes = True


class SystemStats(BaseModel):
    timestamp: str
    cpu_percent: float
    memory_total_mb: float
    memory_used_mb: float
    memory_percent: float
    disk_total_gb: float
    disk_used_gb: float
    disk_percent: float
    bytes_sent_mb: float
    bytes_recv_mb: float
    top_processes: List[Dict[str, Any]]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post(
    "/expenses/",
    response_model=ExpenseOut,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить новую трату"
)
def create_expense(expense: ExpenseCreate, db=Depends(get_db)):
    try:
        db_expense = Expense(**expense.model_dump())
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
        return db_expense
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get(
    "/expenses/",
    response_model=List[ExpenseOut],
    summary="Получить все траты"
)
def read_expenses(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    return db.query(Expense).offset(skip).limit(limit).all()

@app.get(
    "/system/",
    response_model=SystemStats,
    summary="Текущее состояние сервера (CPU, RAM, Disk, Network, top processes)"
)
def get_system_stats():
    try:
        cpu = psutil.cpu_percent(interval=0.8)

        mem = psutil.virtual_memory()
        mem_total = round(mem.total / (1024**2), 1)      # MB
        mem_used = round(mem.used / (1024**2), 1)
        mem_percent = mem.percent

        disk = psutil.disk_usage('/')
        disk_total = round(disk.total / (1024**3), 1)    # GB
        disk_used = round(disk.used / (1024**3), 1)
        disk_percent = disk.percent

        net = psutil.net_io_counters()
        sent_mb = round(net.bytes_sent / (1024**2), 2)
        recv_mb = round(net.bytes_recv / (1024**2), 2)

        processes = []
        for proc in sorted(
            psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
            key=lambda p: p.info['cpu_percent'] if p.info['cpu_percent'] is not None else 0,
            reverse=True
        )[:5]:
            try:
                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "cpu_percent": round(proc.info['cpu_percent'] or 0, 1),
                    "mem_percent": round(proc.info['memory_percent'] or 0, 1)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return {
            "timestamp": date.today().isoformat() + " " + datetime.datetime.now().strftime("%H:%M:%S"),
            "cpu_percent": cpu,
            "memory_total_mb": mem_total,
            "memory_used_mb": mem_used,
            "memory_percent": mem_percent,
            "disk_total_gb": disk_total,
            "disk_used_gb": disk_used,
            "disk_percent": disk_percent,
            "bytes_sent_mb": sent_mb,
            "bytes_recv_mb": recv_mb,
            "top_processes": processes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting stats: {str(e)}")


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "expense-tracker-vps"}
