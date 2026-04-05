from app import app, db, PostComment, CommunityPost
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_post_comments():
    with app.app_context():
        try:
            # Find all comments with NULL post_id
            broken_comments = PostComment.query.filter(PostComment.post_id.is_(None)).all()
            logger.info(f"Found {len(broken_comments)} comments with NULL post_id")
            
            # Fix each broken comment
            for comment in broken_comments:
                logger.info(f"Fixing comment ID: {comment.id}")
                
                # If it's a reply, get post_id from parent
                if comment.parent_id:
                    parent = PostComment.query.get(comment.parent_id)
                    if parent and parent.post_id:
                        comment.post_id = parent.post_id
                        logger.info(f"  Set post_id to {comment.post_id} from parent")
                    else:
                        # If parent doesn't have post_id, delete the comment
                        logger.warning(f"  Parent comment {comment.parent_id} has no post_id, deleting comment")
                        db.session.delete(comment)
                else:
                    # If it's a top-level comment with no post_id, delete it
                    logger.warning(f"  Top-level comment with no post_id, deleting comment")
                    db.session.delete(comment)
            
            # Commit changes
            db.session.commit()
            logger.info("Database fixed successfully")
            
        except Exception as e:
            logger.error(f"Error fixing database: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_post_comments()
