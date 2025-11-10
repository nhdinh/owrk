"""
Trash Cleanup Scheduled Task
Automatically cleans up old trash items based on configuration
"""

import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.repositories.trash_repository import TrashRepository
from app.models.audit_log import AuditLog, SystemLog
from app.repositories.audit_log_repository import AuditLogRepository

logger = logging.getLogger(__name__)

# Create scheduler
scheduler = AsyncIOScheduler()


def cleanup_trash_items():
    """
    Cleanup task that runs periodically to delete old trash items

    This task:
    1. Cleans up items with permanent_delete_at <= now
    2. Cleans up items based on module/resource trash configs
    """
    db: Session = SessionLocal()
    try:
        repo = TrashRepository(db)
        audit_repo = AuditLogRepository(db)

        total_deleted = 0

        # Step 1: Cleanup scheduled items
        logger.info("Starting scheduled trash cleanup...")
        scheduled_deleted = repo.cleanup_scheduled_items()
        total_deleted += scheduled_deleted
        logger.info(f"Deleted {scheduled_deleted} scheduled items")

        # Step 2: Cleanup based on trash configs
        logger.info("Starting config-based trash cleanup...")
        configs = repo.get_all_trash_configs()

        for config in configs:
            if config.auto_delete_days > 0:
                try:
                    deleted_count = repo.cleanup_old_items(
                        config.module_name,
                        config.resource_type
                    )
                    total_deleted += deleted_count

                    if deleted_count > 0:
                        logger.info(
                            f"Deleted {deleted_count} items for "
                            f"{config.module_name}/{config.resource_type} "
                            f"(older than {config.auto_delete_days} days)"
                        )
                except Exception as e:
                    logger.error(
                        f"Error cleaning up {config.module_name}/{config.resource_type}: {e}"
                    )

        # Create system log
        system_log = SystemLog(
            log_level="INFO",
            module_name="admin",
            message=f"Trash cleanup completed: {total_deleted} items deleted",
            details={
                "scheduled_deleted": scheduled_deleted,
                "total_deleted": total_deleted,
                "configs_processed": len(configs),
            },
        )
        db.add(system_log)
        db.commit()

        logger.info(f"Trash cleanup completed: {total_deleted} total items deleted")

    except Exception as e:
        logger.error(f"Error during trash cleanup: {e}", exc_info=True)

        # Create error system log
        try:
            system_log = SystemLog(
                log_level="ERROR",
                module_name="admin",
                message=f"Trash cleanup failed: {str(e)}",
                details={"error": str(e)},
                stack_trace=str(e),
            )
            db.add(system_log)
            db.commit()
        except Exception as log_error:
            logger.error(f"Error creating system log: {log_error}")

    finally:
        db.close()


def start_scheduler():
    """
    Start the scheduled task scheduler

    Cleanup runs:
    - Every day at 2:00 AM (for scheduled items and config-based cleanup)
    - Every 6 hours (for additional config-based cleanup)
    """
    logger.info("Starting trash cleanup scheduler...")

    # Daily cleanup at 2:00 AM
    scheduler.add_job(
        cleanup_trash_items,
        trigger='cron',
        hour=2,
        minute=0,
        id='trash_cleanup_daily',
        name='Daily Trash Cleanup',
        replace_existing=True,
    )

    # Additional cleanup every 6 hours
    scheduler.add_job(
        cleanup_trash_items,
        trigger='interval',
        hours=6,
        id='trash_cleanup_interval',
        name='Interval Trash Cleanup',
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Trash cleanup scheduler started successfully")


def stop_scheduler():
    """Stop the scheduler"""
    logger.info("Stopping trash cleanup scheduler...")
    scheduler.shutdown()
    logger.info("Trash cleanup scheduler stopped")


# For manual testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Running trash cleanup task manually...")
    cleanup_trash_items()
    logger.info("Manual trash cleanup completed")
