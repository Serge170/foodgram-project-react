  deploy:
    runs-on: ubuntu-latest
    needs: build_and_push_to_docker_hub
    steps:
      - name: executing remote ssh commands to deploy
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USER }}
          key: ${{ secrets.SSH_KEY }}
          passphrase: ${{ secrets.PASSPHRASE }}
          script: |
            cd infra
            sudo docker-compose down
            sudo docker pull pashkavrn/foodgram_frontend:latest
            sudo docker pull pashkavrn/foodgram_backend:latest
            touch .env
            echo DB_ENGINE=${{ secrets.DB_ENGINE }} >> .env
            echo DB_NAME=${{ secrets.DB_NAME }} >> .env
            echo POSTGRES_USER=${{ secrets.POSTGRES_USER }} >> .env
            echo POSTGRES_PASSWORD=${{ secrets.POSTGRES_PASSWORD }} >> .env
            echo DB_HOST=${{ secrets.DB_HOST }} >> .env
            echo DB_PORT=${{ secrets.DB_PORT }} >> .env
            sudo docker-compose up -d

  send_message:
    runs-on: ubuntu-latest
    needs: deploy
    steps:
    - name: send message
      uses: appleboy/telegram-action@master
      with:
        to: ${{ secrets.TELEGRAM_TO }}
        token: ${{ secrets.TELEGRAM_TOKEN }}
        message: ${{ github.workflow }} успешно выполнен!