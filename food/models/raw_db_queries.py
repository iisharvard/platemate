from django.db import connection
from collections import namedtuple


def _namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def query_jobs_for_submissions(submission_ids):
    query = """
    with submissions as (
        select id as submission_id, photo_id from food_submission where id in %(submission_ids)s
    ), photos as (
        select id as photo_id, submissions.submission_id
        from food_photo 
        join submissions on submissions.photo_id = food_photo.id
    ), boxes as (
        select id as box_id, photo_id, submission_id
        from food_box 
        join submissions using (photo_id)
    ), box_filter_jobs as (
        select distinct submission_id, photo_id, job.id as job_id, job.hit_id, job.manager_id, job.creation_time, 'box_filter_job'::text as job_type
        from management_job job
        join food_box_filter_job j on j.job_ptr_id = job.id
        join photos using (photo_id) 
    ), box_draw_jobs as (
        select distinct submission_id, photo_id, job.id as job_id, job.hit_id, job.manager_id, job.creation_time, 'box_draw_job'::text as job_type
        from management_job job
        join food_box_draw_job j on j.job_ptr_id = job.id
        join photos using (photo_id) 
    ), box_vote_jobs as (
        select distinct submission_id, photo_id, job.id as job_id, job.hit_id, job.manager_id, job.creation_time, 'box_vote_job'::text as job_type
        from management_job job
        join food_box_vote_job j on j.job_ptr_id = job.id
        join food_box_vote_job_box_groups fbvjbg on fbvjbg.box_vote_job_id = j.job_ptr_id 
        join food_boxgroup bg on fbvjbg.boxgroup_id = bg.id
        join photos using (photo_id) 
    ), describe_jobs as (	
        select distinct submission_id, photo_id, job.id as job_id, job.hit_id, job.manager_id, job.creation_time, 'describe_job'::text as job_type
        from management_job job
        join food_describe_job j on j.job_ptr_id = job.id
        join boxes using (box_id)
    ), match_jobs as (	
        select distinct submission_id, photo_id, job.id as job_id, job.hit_id, job.manager_id, job.creation_time, 'match_job'::text as job_type
        from management_job job
        join food_match_job j on j.job_ptr_id = job.id
        join boxes using (box_id)
    ), match_vote_jobs as (	
        select distinct submission_id, photo_id, job.id as job_id, job.hit_id, job.manager_id, job.creation_time, 'match_vote_job'::text as job_type
        from management_job job
        join food_match_vote_job j on j.job_ptr_id = job.id
        join food_match_vote_job_ingredient_lists jil on j.job_ptr_id = jil.match_vote_job_id 
        join food_ingredientlist il on il.id = jil.ingredientlist_id 
        join boxes using (box_id)
    ), estimate_jobs as (	
        select distinct submission_id, photo_id, job.id as job_id, job.hit_id, job.manager_id, job.creation_time, 'estimate_job'::text as job_type
        from management_job job
        join food_estimate_job j on j.job_ptr_id = job.id
        join food_ingredient fi on fi.id = j.ingredient_id
        join boxes using (box_id)
    
    ), all_jobs as (
        select * from box_filter_jobs
        union all
        select * from box_draw_jobs
        union all
        select * from box_vote_jobs
        union all
        select * from describe_jobs
        union all
        select * from match_jobs
        union all
        select * from match_vote_jobs
        union all
        select * from estimate_jobs
    )
    select * from all_jobs 
    order by submission_id, creation_time asc
    """
    with connection.cursor() as cursor:
        cursor.execute(query, {'submission_ids': tuple(submission_ids)})
        rows = _namedtuplefetchall(cursor)

    return rows
