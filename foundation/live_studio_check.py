"""One explicitly authorised live Studio API smoke test, without saving drafts."""
import argparse
import getpass
import os
from . import studio_ai

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',default=os.environ.get('KB_DB'))
    p.add_argument('--model',default=os.environ.get('KB_STUDIO_MODEL','gpt-4.1-mini'))
    p.add_argument('--live',action='store_true',help='Authorise one potentially billable API request')
    a=p.parse_args()
    if not a.live or not a.db:
        p.error('Supply --db and --live to authorise one live request')
    os.environ['KB_STUDIO_MODEL']=a.model
    if not os.environ.get('OPENAI_API_KEY'):
        os.environ['OPENAI_API_KEY']=getpass.getpass('OpenAI project API key (hidden): ').strip()
    try:
        row=studio_ai.generate(a.db,'M2','pythagoras','standard',1)[0]
    except (studio_ai.StudioAIUnavailable,ValueError,FileNotFoundError) as exc:
        p.exit(1,'Live smoke test failed: '+str(exc)+'\n')
    print('Live model selection accepted. No draft saved.')
    print(row['question'])
    print('Answer:',row['answer'])
    print('Validation:',row['validation'])

if __name__=='__main__':
    main()
