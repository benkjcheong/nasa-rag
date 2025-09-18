#!/usr/bin/env python3
import os
import glob

keep_files = {
    'PMC6048781', 'PMC10472590', 'PMC11167097', 'PMC6985101', 'PMC6280456',
    'PMC5580210', 'PMC4150462', 'PMC5116466', 'PMC8269219', 'PMC4896697',
    'PMC11831363', 'PMC10926278', 'PMC3792163', 'PMC10607959', 'PMC5018776', 'PMC11484870'
}

for file_path in glob.glob('/Users/safcado/nasa-rag-1/no_abstract_txts/*.txt'):
    filename = os.path.basename(file_path).replace('.txt', '')
    if filename not in keep_files:
        os.remove(file_path)
        print(f"Deleted: {filename}.txt")

print("Done!")