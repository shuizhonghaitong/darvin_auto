FROM image-auth-baseline:e2e-20261105 AS cached-dependencies
FROM python:3.11-slim-bookworm
COPY --from=cached-dependencies /usr/local/lib/python3.11/site-packages/numpy /usr/local/lib/python3.11/site-packages/numpy
COPY --from=cached-dependencies /usr/local/lib/python3.11/site-packages/numpy.libs /usr/local/lib/python3.11/site-packages/numpy.libs
COPY --from=cached-dependencies /usr/local/lib/python3.11/site-packages/numpy-2.4.6.dist-info /usr/local/lib/python3.11/site-packages/numpy-2.4.6.dist-info
COPY --from=cached-dependencies /usr/local/lib/python3.11/site-packages/PIL /usr/local/lib/python3.11/site-packages/PIL
COPY --from=cached-dependencies /usr/local/lib/python3.11/site-packages/pillow.libs /usr/local/lib/python3.11/site-packages/pillow.libs
COPY --from=cached-dependencies /usr/local/lib/python3.11/site-packages/pillow-13.0.0.dist-info /usr/local/lib/python3.11/site-packages/pillow-13.0.0.dist-info
WORKDIR /app
COPY main.py serve_model.py start.sh requirements.txt model_weights.npz weights.sha256 ./
EXPOSE 80
CMD ["./start.sh", "--host", "0.0.0.0", "--port", "80"]
