FROM node:16-alpine

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 4200

# Command to run the application in development mode
CMD ["npm", "start", "--", "--host", "0.0.0.0", "--disable-host-check"] 