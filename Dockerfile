FROM 812206152185.dkr.ecr.us-west-2.amazonaws.com/latch-base:6839-main

RUN python3 -m pip install biopython xmltramp2
COPY iprscan5_urllib3.py /root/iprscan5_urllib3.py
COPY iprscan.sh /root/iprscan.sh

COPY wf /root/wf
ARG tag
ENV FLYTE_INTERNAL_IMAGE $tag
RUN python3 -m pip install --upgrade latch
WORKDIR /root
