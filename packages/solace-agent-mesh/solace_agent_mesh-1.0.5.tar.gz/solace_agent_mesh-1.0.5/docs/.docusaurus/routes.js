import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/solace-agent-mesh/docs',
    component: ComponentCreator('/solace-agent-mesh/docs', '495'),
    routes: [
      {
        path: '/solace-agent-mesh/docs',
        component: ComponentCreator('/solace-agent-mesh/docs', '039'),
        routes: [
          {
            path: '/solace-agent-mesh/docs',
            component: ComponentCreator('/solace-agent-mesh/docs', '0fb'),
            routes: [
              {
                path: '/solace-agent-mesh/docs/documentation/concepts/agents',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/concepts/agents', '1da'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/concepts/architecture',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/concepts/architecture', '62a'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/concepts/cli',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/concepts/cli', 'a43'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/concepts/gateways',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/concepts/gateways', '4a2'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/concepts/orchestrator',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/concepts/orchestrator', '4bf'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/concepts/plugins',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/concepts/plugins', '1a4'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/deployment/debugging',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/deployment/debugging', '03d'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/deployment/deploy',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/deployment/deploy', '92b'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/deployment/observability',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/deployment/observability', '77b'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/enterprise',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/enterprise', 'a6d'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/getting-started/component-overview',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/getting-started/component-overview', '042'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/getting-started/installation',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/getting-started/installation', '82c'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/getting-started/introduction',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/getting-started/introduction', 'f14'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/getting-started/quick-start',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/getting-started/quick-start', 'e0d'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/tutorials/bedrock-agents',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/tutorials/bedrock-agents', 'ef0'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/tutorials/custom-agent',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/tutorials/custom-agent', 'dca'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/tutorials/event-mesh-gateway',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/tutorials/event-mesh-gateway', '7e1'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/tutorials/mcp-integration',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/tutorials/mcp-integration', '613'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/tutorials/mongodb-integration',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/tutorials/mongodb-integration', '752'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/tutorials/rag-integration',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/tutorials/rag-integration', 'bfd'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/tutorials/rest-gateway',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/tutorials/rest-gateway', '368'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/tutorials/slack-integration',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/tutorials/slack-integration', 'ae7'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/tutorials/sql-database',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/tutorials/sql-database', 'ae4'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/user-guide/builtin-tools/',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/user-guide/builtin-tools/', '7ae'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/user-guide/builtin-tools/artifact-management',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/user-guide/builtin-tools/artifact-management', '48a'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/user-guide/builtin-tools/audio-tools',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/user-guide/builtin-tools/audio-tools', '329'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/user-guide/builtin-tools/data-analysis-tools',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/user-guide/builtin-tools/data-analysis-tools', 'b18'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/user-guide/builtin-tools/embeds',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/user-guide/builtin-tools/embeds', 'b6f'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/user-guide/create-agents',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/user-guide/create-agents', '0a7'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/user-guide/create-gateways',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/user-guide/create-gateways', 'c31'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/user-guide/creating-service-providers',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/user-guide/creating-service-providers', '069'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/user-guide/solace-ai-connector',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/user-guide/solace-ai-connector', '61b'),
                exact: true,
                sidebar: "docSidebar"
              },
              {
                path: '/solace-agent-mesh/docs/documentation/user-guide/structure',
                component: ComponentCreator('/solace-agent-mesh/docs/documentation/user-guide/structure', 'dec'),
                exact: true,
                sidebar: "docSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
