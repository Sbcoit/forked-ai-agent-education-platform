"""
Cohorts API endpoints for educational group management
Handles cohort creation, student enrollment, and simulation assignments
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, desc, func
from sqlalchemy.sql.functions import coalesce
from typing import List, Optional
from datetime import datetime
import secrets

from database.connection import get_db
from utilities.auth import get_current_user, require_admin
from database.models import (
    Cohort, CohortStudent, CohortSimulation, User, UserProgress, Scenario, generate_cohort_id
)
from database.schemas import (
    CohortCreate, CohortUpdate, CohortResponse, CohortListResponse,
    CohortStudentCreate, CohortStudentUpdate, CohortStudentResponse,
    CohortSimulationCreate, CohortSimulationUpdate, CohortSimulationResponse
)

router = APIRouter(prefix="/cohorts", tags=["Cohorts"])

# --- COHORT CRUD ENDPOINTS ---

@router.get("/", response_model=List[CohortListResponse])
async def get_cohorts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """Get all cohorts with optional filtering"""
    query = db.query(Cohort)
    
    # Filter by creator (users can only see their own cohorts unless admin)
    if current_user.role != "admin":
        query = query.filter(Cohort.created_by == current_user.id)
    
    # Apply search filter
    if search:
        query = query.filter(
            or_(
                Cohort.title.ilike(f"%{search}%"),
                Cohort.description.ilike(f"%{search}%"),
                Cohort.course_code.ilike(f"%{search}%")
            )
        )
    
    # Apply status filter
    if status:
        if status == "active":
            query = query.filter(Cohort.is_active == True)
        elif status == "inactive":
            query = query.filter(Cohort.is_active == False)
    
    # Create subqueries for counts
    student_count_subquery = db.query(
        CohortStudent.cohort_id,
        func.count(CohortStudent.id).label('student_count')
    ).filter(
        CohortStudent.status == "approved"
    ).group_by(CohortStudent.cohort_id).subquery()
    
    simulation_count_subquery = db.query(
        CohortSimulation.cohort_id,
        func.count(CohortSimulation.id).label('simulation_count')
    ).group_by(CohortSimulation.cohort_id).subquery()
    
    # Main query with left joins to get counts in single query
    cohorts_with_counts = query.outerjoin(
        student_count_subquery,
        Cohort.id == student_count_subquery.c.cohort_id
    ).outerjoin(
        simulation_count_subquery,
        Cohort.id == simulation_count_subquery.c.cohort_id
    ).add_columns(
        coalesce(student_count_subquery.c.student_count, 0).label('student_count'),
        coalesce(simulation_count_subquery.c.simulation_count, 0).label('simulation_count')
    ).offset(skip).limit(limit).all()
    
    # Build response with counts from single query
    result = []
    for cohort_row in cohorts_with_counts:
        cohort = cohort_row[0]  # The Cohort object is first in the tuple
        student_count = cohort_row[1]  # student_count from coalesce
        simulation_count = cohort_row[2]  # simulation_count from coalesce
        
        result.append(CohortListResponse(
            id=cohort.id,
            unique_id=cohort.unique_id,
            title=cohort.title,
            description=cohort.description,
            course_code=cohort.course_code,
            semester=cohort.semester,
            year=cohort.year,
            max_students=cohort.max_students,
            is_active=cohort.is_active,
            created_by=cohort.created_by,
            created_at=cohort.created_at,
            student_count=student_count,
            simulation_count=simulation_count
        ))
    
    return result

@router.get("/{cohort_unique_id}", response_model=CohortResponse)
async def get_cohort(
    cohort_unique_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific cohort with students and simulations"""
    cohort = db.query(Cohort).filter(Cohort.unique_id == cohort_unique_id).first()
    if not cohort:
        raise HTTPException(status_code=404, detail="Cohort not found")
    
    # Check permissions (creator or admin)
    if cohort.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this cohort")
    
    # Get students with user details
    students_query = db.query(CohortStudent, User).join(
        User, CohortStudent.student_id == User.id
    ).filter(CohortStudent.cohort_id == cohort.id)
    
    students = []
    for cohort_student, user in students_query:
        students.append(CohortStudentResponse(
            id=cohort_student.id,
            student_id=cohort_student.student_id,
            student_name=user.full_name,
            student_email=user.email,
            status=cohort_student.status,
            enrollment_date=cohort_student.enrollment_date,
            approved_at=cohort_student.approved_at
        ))
    
    # Get simulations
    simulations_query = db.query(CohortSimulation).filter(
        CohortSimulation.cohort_id == cohort.id
    )
    
    simulations = []
    for cohort_simulation in simulations_query:
        simulations.append(CohortSimulationResponse(
            id=cohort_simulation.id,
            simulation_id=cohort_simulation.simulation_id,
            assigned_by=cohort_simulation.assigned_by,
            assigned_at=cohort_simulation.assigned_at,
            due_date=cohort_simulation.due_date,
            is_required=cohort_simulation.is_required
        ))
    
    return CohortResponse(
        id=cohort.id,
        unique_id=cohort.unique_id,
        title=cohort.title,
        description=cohort.description,
        course_code=cohort.course_code,
        semester=cohort.semester,
        year=cohort.year,
        max_students=cohort.max_students,
        auto_approve=cohort.auto_approve,
        allow_self_enrollment=cohort.allow_self_enrollment,
        is_active=cohort.is_active,
        created_by=cohort.created_by,
        created_at=cohort.created_at,
        updated_at=cohort.updated_at,
        students=students,
        simulations=simulations
    )

@router.post("/", response_model=CohortResponse)
async def create_cohort(
    cohort_data: CohortCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new cohort"""
    # Validate max_students if provided
    if cohort_data.max_students is not None and cohort_data.max_students <= 0:
        raise HTTPException(status_code=400, detail="Max students must be positive")
    
    # Generate short, user-friendly ID for the cohort
    unique_id = generate_cohort_id()
    
    # Create cohort
    cohort = Cohort(
        unique_id=unique_id,
        title=cohort_data.title,
        description=cohort_data.description,
        course_code=cohort_data.course_code,
        semester=cohort_data.semester,
        year=cohort_data.year,
        max_students=cohort_data.max_students,
        auto_approve=cohort_data.auto_approve,
        allow_self_enrollment=cohort_data.allow_self_enrollment,
        created_by=current_user.id
    )
    
    db.add(cohort)
    db.commit()
    db.refresh(cohort)
    
    return CohortResponse(
        id=cohort.id,
        unique_id=cohort.unique_id,
        title=cohort.title,
        description=cohort.description,
        course_code=cohort.course_code,
        semester=cohort.semester,
        year=cohort.year,
        max_students=cohort.max_students,
        auto_approve=cohort.auto_approve,
        allow_self_enrollment=cohort.allow_self_enrollment,
        is_active=cohort.is_active,
        created_by=cohort.created_by,
        created_at=cohort.created_at,
        updated_at=cohort.updated_at,
        students=[],
        simulations=[]
    )

@router.put("/{cohort_unique_id}", response_model=CohortResponse)
async def update_cohort(
    cohort_unique_id: str,
    cohort_data: CohortUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a cohort"""
    cohort = db.query(Cohort).filter(Cohort.unique_id == cohort_unique_id).first()
    if not cohort:
        raise HTTPException(status_code=404, detail="Cohort not found")
    
    # Check permissions
    if cohort.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this cohort")
    
    # Update fields
    update_data = cohort_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cohort, field, value)
    
    db.commit()
    db.refresh(cohort)
    
    # Return updated cohort (simplified response)
    return CohortResponse(
        id=cohort.id,
        title=cohort.title,
        description=cohort.description,
        course_code=cohort.course_code,
        semester=cohort.semester,
        year=cohort.year,
        max_students=cohort.max_students,
        auto_approve=cohort.auto_approve,
        allow_self_enrollment=cohort.allow_self_enrollment,
        is_active=cohort.is_active,
        created_by=cohort.created_by,
        created_at=cohort.created_at,
        updated_at=cohort.updated_at,
        students=[],
        simulations=[]
    )

@router.delete("/{cohort_unique_id}")
async def delete_cohort(
    cohort_unique_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a cohort and all related data"""
    cohort = db.query(Cohort).filter(Cohort.unique_id == cohort_unique_id).first()
    if not cohort:
        raise HTTPException(status_code=404, detail="Cohort not found")
    
    # Check permissions
    if cohort.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this cohort")
    
    try:
        # Get counts before deletion for logging
        student_count = db.query(CohortStudent).filter(CohortStudent.cohort_id == cohort.id).count()
        simulation_count = db.query(CohortSimulation).filter(CohortSimulation.cohort_id == cohort.id).count()
        
        # Check if there are any active simulations that might cause issues
        active_simulations = db.query(CohortSimulation).filter(
            CohortSimulation.cohort_id == cohort.id
        ).all()
        
        # Delete related records first to ensure clean deletion
        # This is more explicit than relying only on cascade
        for simulation in active_simulations:
            db.delete(simulation)
        
        # Delete student enrollments
        student_enrollments = db.query(CohortStudent).filter(CohortStudent.cohort_id == cohort.id).all()
        for enrollment in student_enrollments:
            db.delete(enrollment)
        
        # Finally delete the cohort itself
        db.delete(cohort)
        db.commit()
        
        # Log the deletion for audit purposes
        print(f"Cohort '{cohort.title}' (ID: {cohort.unique_id}) deleted by user {current_user.id}")
        print(f"Deleted {student_count} student enrollments and {simulation_count} simulation assignments")
        
        return {
            "message": "Cohort deleted successfully",
            "deleted_students": student_count,
            "deleted_simulations": simulation_count
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error deleting cohort {cohort.unique_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete cohort. Please try again.")

# --- STUDENT MANAGEMENT ENDPOINTS ---

@router.get("/{cohort_unique_id}/students", response_model=List[CohortStudentResponse])
async def get_cohort_students(
    cohort_unique_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all students in a cohort"""
    # Check if cohort exists and user has access
    cohort = db.query(Cohort).filter(Cohort.unique_id == cohort_unique_id).first()
    if not cohort:
        raise HTTPException(status_code=404, detail="Cohort not found")
    
    if cohort.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this cohort")
    
    # Get students
    students_query = db.query(CohortStudent, User).join(
        User, CohortStudent.student_id == User.id
    ).filter(CohortStudent.cohort_id == cohort.id)
    
    students = []
    for cohort_student, user in students_query:
        students.append(CohortStudentResponse(
            id=cohort_student.id,
            student_id=cohort_student.student_id,
            student_name=user.full_name,
            student_email=user.email,
            status=cohort_student.status,
            enrollment_date=cohort_student.enrollment_date,
            approved_at=cohort_student.approved_at
        ))
    
    return students

@router.post("/{cohort_id}/students", response_model=CohortStudentResponse)
async def add_student_to_cohort(
    cohort_id: int,
    student_data: CohortStudentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a student to a cohort"""
    # Check if cohort exists and user has access
    cohort = db.query(Cohort).filter(Cohort.id == cohort_id).first()
    if not cohort:
        raise HTTPException(status_code=404, detail="Cohort not found")
    
    if cohort.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to manage this cohort")
    
    # Check if student exists
    student = db.query(User).filter(User.id == student_data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if student is already enrolled
    existing_enrollment = db.query(CohortStudent).filter(
        CohortStudent.cohort_id == cohort_id,
        CohortStudent.student_id == student_data.student_id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(status_code=400, detail="Student is already enrolled in this cohort")
    
    # Create enrollment
    cohort_student = CohortStudent(
        cohort_id=cohort_id,
        student_id=student_data.student_id,
        status=student_data.status
    )
    
    db.add(cohort_student)
    db.commit()
    db.refresh(cohort_student)
    
    return CohortStudentResponse(
        id=cohort_student.id,
        student_id=cohort_student.student_id,
        student_name=student.full_name,
        student_email=student.email,
        status=cohort_student.status,
        enrollment_date=cohort_student.enrollment_date,
        approved_at=cohort_student.approved_at
    )

# --- SIMULATION MANAGEMENT ENDPOINTS ---

@router.get("/{cohort_unique_id}/simulations", response_model=List[CohortSimulationResponse])
async def get_cohort_simulations(
    cohort_unique_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all simulations assigned to a cohort"""
    # Check if cohort exists and user has access
    cohort = db.query(Cohort).filter(Cohort.unique_id == cohort_unique_id).first()
    if not cohort:
        raise HTTPException(status_code=404, detail="Cohort not found")
    
    if cohort.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this cohort")
    
    # Get simulations
    simulations = db.query(CohortSimulation).filter(
        CohortSimulation.cohort_id == cohort.id
    ).all()
    
    result = []
    for simulation in simulations:
        result.append(CohortSimulationResponse(
            id=simulation.id,
            simulation_id=simulation.simulation_id,
            assigned_by=simulation.assigned_by,
            assigned_at=simulation.assigned_at,
            due_date=simulation.due_date,
            is_required=simulation.is_required
        ))
    
    return result

@router.post("/{cohort_id}/simulations", response_model=CohortSimulationResponse)
async def assign_simulation_to_cohort(
    cohort_id: int,
    simulation_data: CohortSimulationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign a simulation to a cohort"""
    # Check if cohort exists and user has access
    cohort = db.query(Cohort).filter(Cohort.id == cohort_id).first()
    if not cohort:
        raise HTTPException(status_code=404, detail="Cohort not found")
    
    if cohort.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to manage this cohort")
    
    # Check if scenario exists
    scenario = db.query(Scenario).filter(Scenario.id == simulation_data.simulation_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Create assignment
    cohort_simulation = CohortSimulation(
        cohort_id=cohort_id,
        simulation_id=simulation_data.simulation_id,
        assigned_by=current_user.id,
        due_date=simulation_data.due_date,
        is_required=simulation_data.is_required
    )
    
    db.add(cohort_simulation)
    db.commit()
    db.refresh(cohort_simulation)
    
    return CohortSimulationResponse(
        id=cohort_simulation.id,
        simulation_id=cohort_simulation.simulation_id,
        assigned_by=cohort_simulation.assigned_by,
        assigned_at=cohort_simulation.assigned_at,
        due_date=cohort_simulation.due_date,
        is_required=cohort_simulation.is_required
    )
