import ideaToText

# we are only going to use this to generate options
# we collect these options, save them into list or JSON
# then use a boilerplate expansion like script to generate a JS file
# something, somehow, we fill up the script file

"""
decisions = [dec1, dec2, dec3, dec4, ... ]
decision_to_snippet = {'dec1': "{...xxx...}"}
"""

if __name__ == '__main__':
    # you can make a sampler based on an ideaToText grammar
    sampler = ideaToText.Sampler('grammars/ColorSleuth')

    # once you have a sampler, you can draw samples
    sample = sampler.singleSample()
    # each sample is "labelled" with the choices that led to the text
    text = sample['text']
    choices = sample['choices']
    rubric = sample['rubric']
    print(text)
    print(rubric)