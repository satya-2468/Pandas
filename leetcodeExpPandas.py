import pandas as pd
import logging
import sys
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers = [logging.StreamHandler(sys.stdout)]
)

logging.info("started Dept salary leetcode problem")
def department_highest_salary(employee: pd.DataFrame, department: pd.DataFrame) -> pd.DataFrame:
#   employee["salary_rank"] = employee.groupby("departmentId")["salary"].rank(method="dense", ascending=False)
#   top_earners = employee.loc[employee['salary_rank']==1]
#   merged=top_earners.merge(department,left_on='departmentId',right_on='id',how='left')
#   result=merged.rename(columns={
#      'name_y':'Department','name_x':'Employee','salary':'Salary'
#   })[['Department','Employee','Salary']]




    mergered_df = employee.merge(department,left_on='departmentId',right_on='id',how='inner')
    highest_salary_df = mergered_df.groupby('departmentId').apply(lambda x: x[x['salary'] == x['salary'].max()])
    result_df = highest_salary_df[['name_y','name_x','salary']]
    result_df.columns=['Department','Employee', 'Salary']
    return highest_salary_df

    # return result





if __name__ == "__main__":
    employee_raw ={
"id":[1,2,3,4,5],
"name":['Joe','Jim','Henry','Sam','Max'],
"salary":[700,900,800,600,900],
"departmentId":[1,1,2,2,1]
  }
    employee=pd.DataFrame(employee_raw)
    dept_raw ={
"id":[1,2],
"name":['IT','Sales']
  }
    department=pd.DataFrame(dept_raw)
    result=  department_highest_salary(employee,department)
    logging.info(f"\n{result}")
