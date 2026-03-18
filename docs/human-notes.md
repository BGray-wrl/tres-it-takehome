<!-- AGENTS SHOULD IGNORE THIS FILE -->
## Overview

- Take in a photo
- Brand name matches?
- ABV is correct?
- Government warning is there?
- just making sure the number on the form is the same as the number on the label
- handle batch uploads
- there's PII considerations, document retention policies
    - But for a prototype? Just don't do anything crazy. We're not storing anything sensitive for this exercise.
- Oh, and our network blocks outbound traffic to a lot of domains, so keep that in mind if you're thinking about cloud APIs
- the warning statement check is actually trickier than it sounds. It has to be exact. Like, word-for-word, and the 'GOVERNMENT WARNING:' part has to be in all caps and bold
- Smaller font, different wording, burying it in tiny text. I caught one last month where they used 'Government Warning' in title case instead of all caps.
- it would be amazing if the tool could handle images that aren't perfectly shot. I've seen labels that are photographed at weird angles, or the lighting is bad, or there's glare on the bottle. Right now if an agent can't read the label they just reject it and ask for a better image.



### Copied text About TTB Label Requirements
For reference, TTB requires specific information on alcohol beverage labels. The exact requirements vary by beverage type (beer, wine, distilled spirits) but common elements include:
- Brand name
- Class/type designation
- Alcohol content (with some exceptions for certain wine/beer)
- Net contents
- Name and address of bottler/producer
- Country of origin for imports
- **Government Health Warning Statement** (mandatory on all alcohol beverages)