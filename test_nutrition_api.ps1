# Test script for AI nutrition endpoint

$uri = "http://localhost:8000/en/api/v1/ai/nutrition/"

$body = @{
    species = "dog"
    breed = "Golden Retriever"
    breed_size_category = "large"
    age_years = 3.5
    life_stage = "adult"
    weight_kg = 29.0
    body_condition_score = 4
    sex = "male"
    neutered = $true
    activity_level = "moderate"
    health_goal = "weight_loss"
}

$jsonBody = $body | ConvertTo-Json

Write-Host "Testing AI Nutrition Endpoint..." -ForegroundColor Cyan
Write-Host "URL: $uri" -ForegroundColor Yellow
Write-Host ""
Write-Host "Request Body:" -ForegroundColor Yellow
Write-Host $jsonBody

Write-Host ""
Write-Host "Sending request..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri $uri -Method Post -Body $jsonBody -ContentType "application/json"
    
    Write-Host ""
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Response:" -ForegroundColor Yellow
    $response | ConvertTo-Json -Depth 10
    
    Write-Host ""
    Write-Host "Key Results:" -ForegroundColor Cyan
    Write-Host "  Calories per day: $($response.calories_per_day)" -ForegroundColor White
    Write-Host "  Diet style: $($response.diet_style)" -ForegroundColor White
    Write-Host "  Weight risk: $($response.risks.weight_risk)" -ForegroundColor White
    Write-Host "  Model version: $($response.model_version)" -ForegroundColor White
    
} catch {
    Write-Host ""
    Write-Host "FAILED!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.ErrorDetails.Message) {
        Write-Host ""
        Write-Host "Server Response:" -ForegroundColor Yellow
        Write-Host $_.ErrorDetails.Message
    }
}
