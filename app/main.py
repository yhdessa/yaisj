from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, Float, String, Date
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, Field
from datetime import date
from typing import List, Dict, Any
import psutil

# Логирование
from .logger import logger

app = FastAPI(
    title="Expense Tracker VPS",
    description="Personal expense tracker with real-time server monitoring",
    version="0.2.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Логирование всех HTTP-запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        client_host=request.client.host if request.client else None,
    )
    return response


# ====================== Database ======================
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


# ====================== Pydantic Models ======================
class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class ExpenseOut(ExpenseCreate):
    id: int
    date: date

    class Config:
        from_attributes = True


# ====================== DB Dependency ======================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ====================== Endpoints ======================

@app.post("/expenses/", response_model=ExpenseOut, status_code=201)
async def create_expense(expense: ExpenseCreate, db=Depends(get_db)):
    try:
        db_expense = Expense(**expense.model_dump())
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)

        logger.info("expense_created", 
                   expense_id=db_expense.id,
                   amount=expense.amount,
                   category=expense.category)

        return db_expense
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("expense_creation_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Database error")


@app.get("/expenses/", response_model=List[ExpenseOut])
async def read_expenses(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    expenses = db.query(Expense).offset(skip).limit(limit).all()
    logger.info("expenses_retrieved", count=len(expenses))
    return expenses


@app.delete("/expenses/{expense_id}", status_code=204)
async def delete_expense(expense_id: int, db=Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        logger.warning("expense_not_found", expense_id=expense_id)
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()
    logger.info("expense_deleted", expense_id=expense_id)
    return None


@app.put("/expenses/{expense_id}", response_model=ExpenseOut)
async def update_expense(expense_id: int, updated: ExpenseCreate, db=Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        logger.warning("expense_not_found_for_update", expense_id=expense_id)
        raise HTTPException(status_code=404, detail="Expense not found")

    expense.amount = updated.amount
    expense.category = updated.category
    expense.description = updated.description

    db.commit()
    db.refresh(expense)

    logger.info("expense_updated", 
               expense_id=expense.id,
               new_amount=updated.amount,
               new_category=updated.category)

    return expense


@app.get("/system/")
async def get_system_stats():
    try:
        cpu = psutil.cpu_percent(interval=0.8)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()

        stats = {
            "timestamp": date.today().isoformat(),
            "cpu_percent": cpu,
            "memory_total_mb": round(mem.total / (1024**2), 1),
            "memory_used_mb": round(mem.used / (1024**2), 1),
            "memory_percent": mem.percent,
            "disk_total_gb": round(disk.total / (1024**3), 1),
            "disk_used_gb": round(disk.used / (1024**3), 1),
            "disk_percent": disk.percent,
            "bytes_sent_mb": round(net.bytes_sent / (1024**2), 2),
            "bytes_recv_mb": round(net.bytes_recv / (1024**2), 2),
        }

        logger.info("system_stats_retrieved", cpu=cpu, memory=mem.percent)
        return stats

    except Exception as e:
        logger.error("system_stats_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error collecting stats")


@app.get("/health")
async def health_check():
    logger.debug("health_check_called")
    return {"status": "healthy", "service": "expense-tracker-vps"}
