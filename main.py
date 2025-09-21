import config
from git_services import get_git_service
from analysis_engine import get_analysis_engine
import sys

def run_analysis():
    print("Initiating pull request review process.")
    
    try:
        git_service = get_git_service()
        analysis_engine = get_analysis_engine()
        
        print(f"Fetching diff for PR #{config.PR_NUMBER} from '{config.REPO_OWNER}/{config.REPO_NAME}'.")
        
        diff_text = git_service.get_pull_request_diff(config.PR_NUMBER)
        
        if not diff_text:
            print("Error: Could not fetch diff. Verify repository details, PR number, and token.", file=sys.stderr)
            return

        print("Diff fetch successful.")
        print("Submitting code for analysis.")
        
        analysis_result = analysis_engine.analyze_code_changes(diff_text)
        
        if "Could not perform analysis" in analysis_result:
            print(f"Error: {analysis_result}", file=sys.stderr)
            return
            
        print("Analysis received.")
        print("--- Analysis Report ---")
        print(analysis_result)
        print("-----------------------")
        
        git_service.post_review_comment(config.PR_NUMBER, analysis_result)
        
        print("Process completed successfully.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    run_analysis()
