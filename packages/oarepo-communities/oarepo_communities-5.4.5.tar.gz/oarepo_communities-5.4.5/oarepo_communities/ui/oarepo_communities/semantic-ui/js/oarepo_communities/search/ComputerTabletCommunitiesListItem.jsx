// This file is part of InvenioRDM
// Copyright (C) 2022 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/oarepo_dashboard";
import React from "react";
import { Image } from "react-invenio-forms";
import { Grid, Icon, Header } from "semantic-ui-react";
import PropTypes from "prop-types";
import { CommunityTypeLabel } from "./CommunityTypeLabel";
import { RestrictedLabel } from "./RestrictedLabel";

export const ComputerTabledCommunitiesListItem = ({
  result,
  communityTypeLabelTransparent,
  isRestricted,
}) => {
  const communityType = result.ui?.type?.title_l10n;

  return (
    <Grid className="computer tablet only item result-list-item community rel-mb-1 rel-p-1">
      <Grid.Column width={16} verticalAlign="middle" className="pl-0">
        <div className="flex align-items-center">
          <Image
            wrapped
            src={result.links.logo}
            size="small"
            className="community-image rel-mr-2"
            alt=""
          />
          {/* TODO: where to put this style? */}
          <div style={{ flexShrink: 100 }}>
            {isRestricted && (
              <div className="rel-mb-1">
                <RestrictedLabel />
              </div>
            )}
            <Header as="h4">
              <a className="truncate-lines-2" href={result?.links?.self_html}>
                {result.metadata.title}
              </a>
            </Header>
            {result.metadata.description && (
              <p className="truncate-lines-2 text size small text-muted mt-5">
                {result.metadata.description}
              </p>
            )}

            {(communityType ||
              result.metadata.website ||
              result.metadata.organizations) && (
              <div className="wrap mt-5 text size small text-muted">
                {communityType && (
                  <CommunityTypeLabel
                    transparent={communityTypeLabelTransparent}
                    type={communityType}
                  />
                )}

                {result.metadata.website && (
                  <div className="rel-mt-1">
                    <Icon name="linkify" />
                    <a
                      href={result.metadata.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-muted"
                    >
                      {result.metadata.website}
                    </a>
                  </div>
                )}

                {result.metadata.organizations && (
                  <div>
                    <Icon name="building outline" />
                    {result.metadata.organizations.map((org, index) => {
                      const separator = (index > 0 && ", ") || "";

                      return (
                        <span className="text-muted" key={org.name}>
                          {separator}
                          {org.name}
                          {org.id && (
                            <a
                              href={`https://ror.org/${org.id}`}
                              aria-label={`${org.name}'s ROR ${i18next.t(
                                "profile"
                              )}`}
                              title={`${org.name}'s ROR ${i18next.t(
                                "profile"
                              )}`}
                              target="_blank"
                              rel="noreferrer"
                            >
                              <img
                                className="inline-id-icon ml-5"
                                src="/static/images/ror-icon.svg"
                                alt=""
                              />
                            </a>
                          )}
                        </span>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </Grid.Column>
    </Grid>
  );
};

ComputerTabledCommunitiesListItem.propTypes = {
  result: PropTypes.object.isRequired,
  communityTypeLabelTransparent: PropTypes.bool,
  isRestricted: PropTypes.bool,
};
