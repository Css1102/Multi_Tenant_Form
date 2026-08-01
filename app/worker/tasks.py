import os
import csv
from sqlmodel import Session, select
from .celery import celery_app
from app.database import engine
from app.models import Form, FormSubmission
EXPORT_DIR = "secure_exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

@celery_app.task(bind=True, name="generate_csv_export")
def generate_csv_export(self, form_id: str, tenant_id: str):
    """
    Queries the database in real-time, builds a CSV from dynamic JSONB fields, 
    and saves it to the disk.
    """
    file_path = os.path.join(EXPORT_DIR, f"export_{tenant_id}_{form_id}.csv")
    
    with Session(engine) as session:
        
        form = session.get(Form, form_id)
        if not form or str(form.organization_id) != tenant_id:
            return {"status": "error", "message": "Unauthorized or Form not found"}
            
        # Extract headers dynamically from your JSONB structure definition
        # e.g., ["Submission ID", "Submitted At", "First Name", "Age"]
        dynamic_headers = [field.label for field in form.structure]
        csv_headers = ["Submission ID", "Submitted At"] + dynamic_headers
        
        # 3. Fetch all submissions for this form
        # For MASSIVE datasets (1M+ rows), you would use session.yield_per(1000) here
        statement = select(FormSubmission).where(FormSubmission.form_id == form_id)
        submissions = session.exec(statement).all()
        total_rows = len(submissions)
        
        if total_rows == 0:
             return {"status": "success", "message": "No submissions found."}

        # 4. Open the CSV file and start streaming data to it
        with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(csv_headers) # Write the top row
            
            for index, sub in enumerate(submissions):
                # Start the row with standard relational data
                row = [str(sub.id), sub.created_at.isoformat()]
                
                # Loop through the dynamic schema and safely extract JSONB answers
                for field in form.structure:
                    # If the user didn't answer an optional field, default to an empty string
                    answer_value = sub.answers.get(field.id, "")
                    row.append(answer_value)
                    
                writer.writerow(row)
                
                # 5. Update Celery Progress every 100 rows
                if index % 100 == 0:
                    progress_pct = int((index / total_rows) * 100)
                    self.update_state(state='PROCESSING', meta={'progress': progress_pct})
                    
    # The task is done! Return a URL where the frontend can download the generated file.
    download_url = f"/exports/download/{tenant_id}_{form_id}.csv"
    
    return {"status": "success", "download_url": download_url}
