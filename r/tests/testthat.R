library(testthat)

test_that("attribution schema columns are defined", {
  source("../R/io_contract.R")
  expect_equal(
    ATTRIBUTION_SCHEMA_COLUMNS,
    c(
      "method", "engine", "dag_variant", "iteration_round",
      "feature", "attribution_value", "run_id", "git_sha", "timestamp"
    )
  )
})
