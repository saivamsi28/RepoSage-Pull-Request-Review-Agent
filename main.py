import config
from git_services import GitServiceFactory
from analysis_engine import get_analysis_engine
import sys
import argparse
import json
from datetime import datetime

class PRReviewOrchestrator:
    def __init__(self, git_server='github'):
        self.git_server = git_server
        self.git_service = None
        self.analysis_engine = None
        
    def initialize_services(self):
        try:
            self.git_service = GitServiceFactory.create_service(self.git_server)
            self.git_service.set_repository(config.REPO_OWNER, config.REPO_NAME)
            self.analysis_engine = get_analysis_engine()
            return True
        except Exception as e:
            print(f"Service initialization failed: {e}", file=sys.stderr)
            return False
    
    def fetch_pr_diff(self, pr_number):
        print(f"Retrieving diff for {self.git_server} PR #{pr_number}")
        print(f"Repository: {config.REPO_OWNER}/{config.REPO_NAME}")
        
        diff_text = self.git_service.get_pull_request_diff(pr_number)
        
        if not diff_text:
            print("Failed to retrieve diff. Verify repository access and PR number.", file=sys.stderr)
            return None
        
        print(f"Successfully retrieved diff ({len(diff_text)} characters)")
        return diff_text
    
    def analyze_changes(self, diff_text, review_depth='standard'):
        print("Submitting code for AI analysis...")
        
        review_extension = ""
        if review_depth == 'comprehensive':
            review_extension = "Perform deep architectural analysis and design pattern review."
        elif review_depth == 'security':
            review_extension = "Focus on security vulnerabilities and data protection."
        
        analysis_result = self.analysis_engine.analyze_code_changes(diff_text, review_extension)
        
        if "Unable to analyze" in analysis_result or "Analysis failed" in analysis_result:
            print(f"Analysis error: {analysis_result}", file=sys.stderr)
            return None
        
        print("Analysis completed successfully")
        return analysis_result
    
    def post_review(self, pr_number, analysis_result):
        success = self.git_service.post_review_comment(pr_number, analysis_result)
        
        if success:
            print(f"Review posted to {self.git_server} PR #{pr_number}")
        else:
            print("Failed to post review comment", file=sys.stderr)
        
        return success
    
    def generate_report(self, pr_number, analysis_result, metadata=None):
        report = {
            'timestamp': datetime.now().isoformat(),
            'git_server': self.git_server,
            'repository': f"{config.REPO_OWNER}/{config.REPO_NAME}",
            'pr_number': pr_number,
            'analysis': analysis_result,
            'metadata': metadata or {}
        }
        
        return report

def run_batch_analysis(pr_numbers, git_server='github'):
    orchestrator = PRReviewOrchestrator(git_server)
    
    if not orchestrator.initialize_services():
        return False
    
    results = []
    
    for pr_number in pr_numbers:
        print(f"\n{'='*50}")
        print(f"Processing PR #{pr_number}")
        print(f"{'='*50}")
        
        diff_text = orchestrator.fetch_pr_diff(pr_number)
        if not diff_text:
            results.append({'pr_number': pr_number, 'status': 'failed', 'error': 'Could not fetch diff'})
            continue
        
        analysis = orchestrator.analyze_changes(diff_text)
        if not analysis:
            results.append({'pr_number': pr_number, 'status': 'failed', 'error': 'Analysis failed'})
            continue
        
        report = orchestrator.generate_report(pr_number, analysis)
        results.append({'pr_number': pr_number, 'status': 'success', 'report': report})
        
        print("\n--- Analysis Report ---")
        print(analysis)
        print("-----------------------\n")
        
        orchestrator.post_review(pr_number, analysis)
    
    return results

def main():
    parser = argparse.ArgumentParser(description='RepoSage - AI-Powered Pull Request Review Agent')
    parser.add_argument('--git-server', choices=['github', 'gitlab', 'bitbucket'], 
                       default='github', help='Git server platform')
    parser.add_argument('--pr-numbers', nargs='+', type=int, 
                       help='Pull request numbers to analyze')
    parser.add_argument('--review-depth', choices=['standard', 'comprehensive', 'security'],
                       default='standard', help='Depth of code review')
    parser.add_argument('--output', choices=['console', 'json', 'file'],
                       default='console', help='Output format')
    parser.add_argument('--output-file', help='Output file path (when --output=file)')
    
    args = parser.parse_args()
    
    pr_numbers = args.pr_numbers or [int(config.PR_NUMBER)] if config.PR_NUMBER else []
    
    if not pr_numbers:
        print("Error: No pull request numbers provided", file=sys.stderr)
        return 1
    
    print("RepoSage Pull Request Review Agent")
    print(f"Platform: {args.git_server.capitalize()}")
    print(f"Review Depth: {args.review_depth.capitalize()}")
    print(f"PRs to analyze: {pr_numbers}")
    print("")
    
    orchestrator = PRReviewOrchestrator(args.git_server)
    
    if not orchestrator.initialize_services():
        return 1
    
    all_results = []
    
    for pr_number in pr_numbers:
        print(f"\nAnalyzing PR #{pr_number}...")
        
        diff_text = orchestrator.fetch_pr_diff(pr_number)
        if not diff_text:
            continue
        
        analysis = orchestrator.analyze_changes(diff_text, args.review_depth)
        if not analysis:
            continue
        
        metadata = orchestrator.git_service.get_pr_metadata(pr_number)
        report = orchestrator.generate_report(pr_number, analysis, metadata)
        all_results.append(report)
        
        if args.output == 'console':
            print("\n" + "="*60)
            print(f"ANALYSIS REPORT - PR #{pr_number}")
            print("="*60)
            print(analysis)
            print("="*60 + "\n")
        
        orchestrator.post_review(pr_number, analysis)
    
    if args.output == 'json':
        print(json.dumps(all_results, indent=2))
    elif args.output == 'file' and args.output_file:
        with open(args.output_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"Results written to {args.output_file}")
    
    print("\nAnalysis process completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())